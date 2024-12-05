from flask import Flask, jsonify, request, render_template, redirect, url_for, session, flash
import pymssql
import hashlib
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
import logging

app = Flask(__name__)
app.secret_key = 'clé_secrète'  # Pour gérer les sessions

# Configuration des logs
app.logger.setLevel(logging.DEBUG)

# Configuration de la base de données Azure SQL
server = 'blogfilm.database.windows.net'
database = 'blogfilms'
username = 'ilyblog'
password = '....'

# Configuration Azure Blob Storage
account_name = 'blogfilmstorage'
account_key = '...'
container_name = 'posters'

blob_service_client = BlobServiceClient(
    account_url=f"https://{account_name}.blob.core.windows.net",
    credential=account_key
)
container_client = blob_service_client.get_container_client(container_name)

# Connexion à la base de données SQL
def get_db_connection():
    conn = pymssql.connect(server, username, password, database)
    return conn

def generate_sas_url(blob_name):
    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=container_name,
        blob_name=blob_name,
        account_key=account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(days=30)  # Valable 30 jours
    )
    return f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/films')
def films():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Si l'utilisateur n'est pas connecté, redirige vers la page de connexion

    # Récupérer la liste des films avec les noms des utilisateurs
    conn = get_db_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('''
        SELECT Films.film_id, Films.title, Films.genre, Films.release_year, Films.image_url, Films.user_id, Users.username
        FROM Films
        JOIN Users ON Films.user_id = Users.user_id
    ''')
    films = cursor.fetchall()
    conn.close()

    # Générer des URL SAS pour chaque image
    for film in films:
        blob_name = film['image_url'].split('/')[-1]  # Nom du fichier
        film['image_url'] = generate_sas_url(blob_name)

    return render_template('films.html', films=films)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Si l'utilisateur n'est pas connecté, redirige vers la page de connexion

    if request.method == 'POST':
        if 'file' not in request.files:
            flash("Aucun fichier trouvé.", "danger")
            return redirect(url_for('upload'))

        file = request.files['file']
        blob_name = file.filename

        try:
            # Upload du fichier dans Azure Blob Storage
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.upload_blob(file.read(), overwrite=True)

            # Enregistrer le film dans la base de données
            conn = get_db_connection()
            cursor = conn.cursor()

            # URL de l'image uploadée
            image_url = blob_client.url

            # Récupérer les données du formulaire
            title = request.form.get('title', 'Titre inconnu')
            genre = request.form.get('genre', 'Genre inconnu')
            release_year = request.form.get('release_year', '2024')  # Par défaut, l'année actuelle
            user_id = session['user_id']  # ID de l'utilisateur connecté

            # Insérer le film dans la base de données avec l'ID utilisateur
            cursor.execute(
                '''
                INSERT INTO Films (title, genre, release_year, user_id, image_url)
                VALUES (%s, %s, %s, %s, %s)
                ''',
                (title, genre, release_year, user_id, image_url)
            )
            conn.commit()
            conn.close()

            return render_template('success.html', message="Film ajouté avec succès.")
        except Exception as e:
            return f"Erreur : {e}", 500

    return render_template('upload.html')

@app.route('/delete/<int:film_id>', methods=['POST'])
def delete_film(film_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirige si non connecté

    user_id = session['user_id']

    # Vérifie si l'utilisateur est bien l'auteur du film
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM Films WHERE film_id = %s', (film_id,))
    film = cursor.fetchone()

    if not film or film[0] != user_id:
        conn.close()
        return "Non autorisé", 403  # Erreur : utilisateur non autorisé

    # Supprime le film de la base de données
    cursor.execute('DELETE FROM Films WHERE film_id = %s', (film_id,))
    conn.commit()
    conn.close()

    return render_template('success.html', message="Film supprimé avec succès.")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()  # On hash le mot de passe pour le sécuriser

        # Vérifier si l'utilisateur existe déjà
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Users WHERE username = %s', (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            return render_template('success.html', message="Utilisateur déjà existant.")
        
        # Insérer le nouvel utilisateur dans la base de données
        cursor.execute('INSERT INTO Users (username, email, password) VALUES (%s, %s, %s)',
                       (username, email, hashed_password))
        conn.commit()
        conn.close()

        return render_template('success.html', message="Compte créé avec succès. Connectez-vous pour continuer.")
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()  # Hash du mot de passe

        # Vérifier les informations de connexion
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Users WHERE username = %s AND password = %s', (username, hashed_password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]  # Stocke l'ID de l'utilisateur dans la session
            return render_template('success.html', message="Connexion réussie !")
        else:
            return render_template('success.html', message="Nom d'utilisateur ou mot de passe incorrect.")

    return render_template('login.html')

@app.route('/logout') 
def logout():
    session.pop('user_id', None)  # Supprime l'utilisateur de la session
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
