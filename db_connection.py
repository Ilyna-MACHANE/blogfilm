import pyodbc

# Remplace par tes informations
server = 'blogfilm.database.windows.net'
database = 'blogfilms'
username = 'ilyblog'
password = 'mdp!'

# Chaîne de connexion
conn_str = 'DRIVER={SQL Server};SERVER=blogfilm.database.windows.net;DATABASE=blogfilms;UID=ilyblog;PWD=mdp'

conn = None  # Définir conn à None pour éviter l'erreur NameError

# Se connecter à la base de données
try:
    conn = pyodbc.connect(conn_str)
    print("Connexion réussie à la base de données Azure SQL !")

    cursor = conn.cursor()

    # Créer une table Users si elle n'existe pas déjà
    cursor.execute('''
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Users')
        BEGIN
            CREATE TABLE Users (
                user_id INT PRIMARY KEY IDENTITY(1,1),
                username VARCHAR(100),
                email VARCHAR(100),
                password VARCHAR(100)
            )
        END
    ''')

    # Créer la table Films si elle n'existe pas
    cursor.execute('''
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Films')
        BEGIN
            CREATE TABLE Films (
                film_id INT PRIMARY KEY IDENTITY(1,1),
                title VARCHAR(255),
                genre VARCHAR(100),
                release_year INT
            )
        END
    ''')

    # Créer la table Reviews si elle n'existe pas
    cursor.execute('''
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Reviews')
        BEGIN
            CREATE TABLE Reviews (
                review_id INT PRIMARY KEY IDENTITY(1,1),
                user_id INT,
                film_id INT,
                review_text TEXT,
                rating INT,
                FOREIGN KEY (user_id) REFERENCES Users(user_id),
                FOREIGN KEY (film_id) REFERENCES Films(film_id)
            )
        END
    ''')

    # Insérer un utilisateur dans la table Users
    cursor.execute('''
        INSERT INTO Users (username, email, password) 
        VALUES (?, ?, ?)
    ''', ('ilyna', 'ilyna@example.com', 'azerty25!'))

    # Ajouter un film dans la table Films
    cursor.execute('''
        INSERT INTO Films (title, genre, release_year)
        VALUES (?, ?, ?)
    ''', ('Inception', 'Sci-Fi', 2010))

    # Ajouter une critique pour ce film
    cursor.execute('''
        INSERT INTO Reviews (user_id, film_id, review_text, rating)
        VALUES (?, ?, ?, ?)
    ''', (1, 1, 'Un film brillant avec une narration complexe!', 5))

    # Confirmer les changements
    conn.commit()
    print("Utilisateur, film et critique ajoutés avec succès.")

    # Lire et afficher tous les utilisateurs
    cursor.execute('SELECT * FROM Users')
    rows = cursor.fetchall()
    print("\nListe des utilisateurs :")
    for row in rows:
        print(f"User ID: {row.user_id}, Username: {row.username}, Email: {row.email}")

    # Lire et afficher tous les films
    cursor.execute('SELECT * FROM Films')
    films = cursor.fetchall()
    print("\nFilms disponibles :")
    for film in films:
        print(f"Film ID: {film.film_id}, Title: {film.title}, Genre: {film.genre}, Year: {film.release_year}")

    # Lire et afficher toutes les critiques
    cursor.execute('SELECT * FROM Reviews')
    reviews = cursor.fetchall()
    print("\nCritiques des films :")
    for review in reviews:
        print(f"Review ID: {review.review_id}, Film ID: {review.film_id}, User ID: {review.user_id}, Rating: {review.rating}, Review: {review.review_text}")

except Exception as e:
    print(f"Erreur de connexion : {e}")
finally:
    if conn:
        conn.close()  # Fermer la connexion si elle a été ouverte
