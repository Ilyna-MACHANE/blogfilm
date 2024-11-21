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

@app.route('/films')
def get_films():
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Films')
        rows = cursor.fetchall()

        films = []
        for row in rows:
            films.append({
                'id': row.film_id,
                'title': row.title,
                'genre': row.genre,
                'year': row.release_year
            })

        return jsonify(films)

    except Exception as e:
        return f"Erreur : {e}"

    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
