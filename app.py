from flask import Flask, jsonify
import pyodbc
import logging

app = Flask(__name__)

# Configuration des logs
app.logger.setLevel(logging.DEBUG)

# Configuration de la base de données Azure SQL
server = 'blogfilm.database.windows.net'
database = 'blogfilms'
username = 'ilyblog'
password = 'azerty25!'
conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

@app.route('/')
def home():
    return "Bienvenue sur mon blog de films !"

@app.route('/films')
def get_films():
    try:
        app.logger.debug("Tentative de connexion à la base de données...")
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Films')
        rows = cursor.fetchall()

        if not rows:
            app.logger.debug("Aucun film trouvé dans la base de données.")
        
        films = []
        for row in rows:
            films.append({
                'id': row.film_id,
                'title': row.title,
                'genre': row.genre,
                'year': row.release_year
            })

        app.logger.debug(f"Films récupérés : {films}")
        return jsonify(films)

    except Exception as e:
        app.logger.error(f"Erreur lors de la récupération des films : {e}")
        return f"Erreur : {e}"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
