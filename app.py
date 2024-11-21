from flask import Flask, jsonify
import pymssql
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
