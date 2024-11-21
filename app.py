from flask import Flask, jsonify
import pyodbc

app = Flask(__name__)

# Configuration de la base de données Azure SQL
server = 'blogfilm.database.windows.net'
database = 'blogfilms'
username = 'ilyblog'
password = 'azerty25!'
conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

@app.route('/')
def home():
    return "Bienvenue sur mon blog de films !"

@app.route('/test-connection')
def test_connection():
    try:
        # Test de la connexion à la base de données
        conn = pyodbc.connect(conn_str)
        return "Connexion réussie à la base de données !"
    except Exception as e:
        return f"Erreur de connexion : {e}"
    finally:
        if conn:
            conn.close()

@app.route('/films')
def get_films():
    try:
        # Se connecter à la base de données
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Exécution de la requête SQL pour récupérer les films
        cursor.execute('SELECT * FROM Films')
        rows = cursor.fetchall()

        # Préparation des données au format JSON
        films = []
        for row in rows:
            films.append({
                'id': row.film_id,
                'title': row.title,
                'genre': row.genre,
                'year': row.release_year
            })

        # Retourner les films sous forme de JSON
        return jsonify(films)

    except Exception as e:
        return f"Erreur de connexion à la base de données : {e}"

    finally:
        if conn:
            conn.close()  # Assure-toi de fermer la connexion

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
