from flask import Flask, jsonify, request, render_template
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
    return render_template('index.html')

@app.route('/films')
def films():
    # Connecte-toi à la base de données et récupère les films
    conn = pymssql.connect(server, username, password, database)
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT * FROM Films')
    films = cursor.fetchall()
    conn.close()

    # Passe les films à la page HTML
    return render_template('films.html', films=films)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
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

# Configuration Azure Blob Storage
account_name = 'blogfilmstorage'  # Exemple : blogfilmstorage
account_key = 'ZYjgrt9jn8otGQHQLjCsQLLJvyuyH8jN9oyRj3qsKDjO+959l0GumABPJy7VVa4jIupYPQSX/2bs+AStQa2mZA=='
container_name = 'posters'

# Créer le client Blob
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
