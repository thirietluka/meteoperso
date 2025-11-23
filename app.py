from flask import Flask, jsonify, render_template, request, redirect, url_for, session, make_response
import psycopg2
import bcrypt

app = Flask(__name__)

# Clé utilisée pour signer les cookies de session Flask
# (Important pour empêcher la falsification)
app.secret_key = "change_moi_secret"


# ----------------------------------------------------
# Sécurisation des en-têtes HTTP pour limiter les attaques
# ----------------------------------------------------
@app.after_request
def set_secure_headers(response):
    # Empêche le chargement de scripts depuis n’importe où
    # Seul "self" + CDN jsdelivr sont autorisés
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; script-src 'self' https://cdn.jsdelivr.net;"
    )

    # Empêche l'inclusion du site dans une iframe (clickjacking)
    response.headers['X-Frame-Options'] = 'DENY'

    # Empêche les interprétations de type MIME dangereuses
    response.headers['X-Content-Type-Options'] = 'nosniff'

    # Empêche l’envoi du header Referer
    response.headers['Referrer-Policy'] = 'no-referrer'

    return response


# ----------------------------------------------------
# Configuration de la base PostgreSQL
# ----------------------------------------------------
DB_HOST = "192.168.0.3"
DB_NAME = "meteoperso_db"
DB_USER = "meteo_user"
DB_PASS = "Bxn89bxn89."


def get_db_connection():
    """
    Retourne une nouvelle connexion PostgreSQL.
    Toujours ouvrir/fermer immédiatement pour éviter les connexions zombies.
    """
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )


def get_connection():
    """
    Même fonction que get_db_connection(), doublon.
    Probablement laissée par commodité ou ancienne version.
    """
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST
    )


# ----------------------------------------------------
# Route: /login
# Gère l’authentification utilisateur
# ----------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():

    # Si déjà connecté → redirection vers le dashboard
    if 'user' in session:
        return redirect(url_for('graphics'))

    # ---------- POST = tentative de connexion ----------
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password'].encode('utf-8')  # password brut

        # Connexion à la DB
        connection = get_connection()
        cursor = connection.cursor()

        # Récupère le hash du password (si le login existe)
        cursor.execute("SELECT password FROM users WHERE login=%s", (login,))
        row = cursor.fetchone()

        cursor.close()
        connection.close()

        # Aucun utilisateur trouvé
        if row is None:
            return render_template('login.html', error="Identifiants invalides")

        try:
            stored_hash = row[0].encode('utf-8')  # Hash stocké en DB

            # Vérifie le mot de passe avec bcrypt
            if bcrypt.checkpw(password, stored_hash):
                # Stocke l’utilisateur dans la session (cookie sécurisé)
                session['user'] = login
                return redirect(url_for('graphics'))
            else:
                return render_template('login.html', error="Identifiants invalides")

        except ValueError:
            # Le cas où le hash en DB n'est pas un vrai hash bcrypt
            print("Hash invalide, mot de passe non hashé en DB ?")
            return render_template('login.html', error="Identifiants invalides")

    # ---------- GET = afficher la page de login ----------
    return render_template('login.html')


# ----------------------------------------------------
# Route: /data
# Récupère les dernières données CPU/RAM/DISK
# pour l’affichage dans les graphiques
# ----------------------------------------------------
@app.route("/data")
def get_data():

    # Accès interdit si pas connecté
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    # Récupère les 60 dernières mesures
    cur.execute("""
        SELECT cpu, ram, disk, created_at
        FROM meteo_table
        ORDER BY created_at DESC
        LIMIT 60;
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    # Convertit le résultat PostgreSQL → JSON
    result = [
        {
            "CPU": r[0],
            "RAM": r[1],
            "DISK": r[2],
            "created_at": r[3].isoformat()
        }
        for r in rows
    ]

    return jsonify(result)


# ----------------------------------------------------
# Route: /graphics
# Affiche la page HTML contenant les graphiques JS
# ----------------------------------------------------
@app.route("/graphics")
def graphics():
    if 'user' not in session:
        return redirect(url_for('login'))

    # Passe le nom d'utilisateur au template
    return render_template("index.html", user=session['user'])


# ----------------------------------------------------
# Route: /logout
# Déconnecte l'utilisateur (supprime la session)
# ----------------------------------------------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


# ----------------------------------------------------
# Route principale
# ----------------------------------------------------
@app.route("/")
def home():
    return redirect(url_for('graphics'))


# ----------------------------------------------------
# Lancement du serveur Flask en HTTPS
# ----------------------------------------------------
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        ssl_context=('meteoperso.luka.local.crt', 'meteoperso.luka.local.key'),
        debug=True
    )
