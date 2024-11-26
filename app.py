from flask import Flask, jsonify, request, render_template, redirect, url_for, session
import pymssql
import hashlib
from azure.storage.blob import BlobServiceClient
import logging

app = Flask(__name__)
app.secret_key = 'ton_clé_secrète'  # Pour gérer les sessions

# Configuration des logs
app.logger.setLevel(logging.DEBUG)

# Configuration de la base de données Azure SQL
server = 'blogfilm.database.windows.net'
database = 'blogfilms'
username = 'ilyblog'
password = 'azerty25!'

# Connexion à la base de données SQL
def get_db_connection():
    conn = pymssql.connect(server, username, password, database)
    return conn

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/films')
def films():
    # Récupérer la liste des films depuis la base de données
    conn = get_db_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Films')
    films = cursor.fetchall()
    conn.close()
    return render_template('films.html', films=films)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Si l'utilisateur n'est pas connecté, redirige vers la page de connexion
    
    if request.method == 'POST':
        if 'file' not in request.files:
            return "Aucun fichier trouvé", 400

        file = request.files['file']
        blob_name = file.filename

        try:
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.upload_blob(file.read(), overwrite=True)
            return "Fichier uploadé avec succès !"
        except Exception as e:
            return f"Erreur : {e}", 500

    return render_template('upload.html')

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
            return "Utilisateur déjà existant", 400
        
        # Insérer le nouvel utilisateur dans la base de données
        cursor.execute('INSERT INTO Users (username, email, password) VALUES (%s, %s, %s)',
                       (username, email, hashed_password))
        conn.commit()
        conn.close()

        return redirect(url_for('login'))  # Rediriger vers la page de connexion après l'inscription
    
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
            return redirect(url_for('home'))
        else:
            return "Nom d'utilisateur ou mot de passe incorrect", 400

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Supprime l'utilisateur de la session
    return redirect(url_for('home'))

# Configuration Azure Blob Storage
account_name = 'blogfilmstorage'
account_key = 'ZYjgrt9jn8otGQHQLjCsQLLJvyuyH8jN9oyRj3qsKDjO+959l0GumABPJy7VVa4jIupYPQSX/2bs+AStQa2mZA=='
container_name = 'posters'

blob_service_client = BlobServiceClient(
    account_url=f"https://{account_name}.blob.core.windows.net",
    credential=account_key
)
container_client = blob_service_client.get_container_client(container_name)

@app.route('/poster/<blob_name>')
def get_poster(blob_name):
    try:
        blob_client = container_client.get_blob_client(blob_name)
        url = blob_client.url
        return jsonify({"url": url})
    except Exception as e:
        app.logger.error(f"Erreur lors de la récupération : {e}")
        return f"Erreur lors de la récupération : {e}", 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
