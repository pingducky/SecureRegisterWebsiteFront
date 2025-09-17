from flask import Flask, render_template, request, redirect, url_for, flash
import math
import string

app = Flask(__name__)
app.secret_key = "secret123"  # nécessaire pour les messages flash

# Utilisateurs fictifs
users = {
    "admin": "password123",
    "user": "pass"
}


def calculate_entropy(password: str) -> float:
    charset_size = 0
    if any(c.islower() for c in password):
        charset_size += 26
    if any(c.isupper() for c in password):
        charset_size += 26
    if any(c.isdigit() for c in password):
        charset_size += 10
    if any(c in string.punctuation for c in password):
        charset_size += 32  # approximation des symboles spéciaux
    entropy = len(password) * math.log2(charset_size or 1)
    return entropy


@app.route("/", methods=["GET", "POST"])
def login():
    entropy = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Calculer l'entropie même si login incorrect
        entropy = calculate_entropy(password)

        if username in users and users[username] == password:
            return f"Bienvenue, {username} ! (Entropie: {entropy:.2f} bits)"
        else:
            flash("Nom d'utilisateur ou mot de passe incorrect")
            return render_template("login.html", entropy=entropy, password=password)

    return render_template("login.html", entropy=entropy)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)