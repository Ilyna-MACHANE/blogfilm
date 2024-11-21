from flask import Flask, jsonify, request
import pymssql
from azure.storage.blob import BlobServiceClient
import logging

app = Flask(__name__)

# Configuration des logs
app.logger.setLevel(logging.DEBUG)

# Configuration de la base de données Azure SQL
server = 'blogfilm.database.windows.net'
database = 'blogfilms'
username = 'ilyblog'
password = 'azerty25!'

@app.route('/')
def home():
    return "Bienvenue sur mon blog de films !"

@app.route('/films')
def get_films():
    try:
        app.logger.debug("Tentative de connexion à la base de données...")
        conn = pymssql.connect(server, username, password, database)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Films')
        rows = cursor.fetchall()

        if not rows:
            app.logger.debug("Aucun film trouvé dans la base de données.")
        
        films = []
        for row in rows:
            films.append(
                {
                'id': row[0],
                'title':  row[1],
                'genre':  row[2],
                'year':  row[3]
                }
            )

        app.logger.debug(f"Films récupérés : {films}")
        return jsonify(films)

    except Exception as e:
        app.logger.error(f"Erreur lors de la récupération des films : {e}")
        return f"Erreur : {e}"

# Configuration Azure Blob Storage
account_name = 'ton-nom-de-compte'  # Exemple : blogfilmstorage
account_key = 'ta-clé-d’accès-principale'
container_name = 'posters'

# Créer le client Blob
blob_service_client = BlobServiceClient(
    account_url=f"https://{account_name}.blob.core.windows.net",
    credential=account_key
)
container_client = blob_service_client.get_container_client(container_name)

@app.route('/upload', methods=['POST'])
def upload_poster():
    if 'file' not in request.files:
        return "Aucun fichier trouvé", 400

    file = request.files['file']
    blob_name = file.filename

    try:
        # Assurez-vous que l'image est bien téléchargée en mode binaire
        blob_client = container_client.get_blob_client(blob_name)
        
        # Upload du fichier en mode binaire
        blob_client.upload_blob(file.stream, overwrite=True)  # Utilisation de .stream pour télécharger le fichier
        return f"Fichier {blob_name} uploadé avec succès !"
    except Exception as e:
        app.logger.error(f"Erreur lors de l'upload du fichier : {e}")
        return f"Erreur lors de l'upload : {e}", 500





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
    app.run(debug=True, host='0.0.0.0', port=80)
