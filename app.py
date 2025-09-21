from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
import math
import string

app = Flask(__name__)
app.secret_key = "une_clé_bien_longue_et_secrète"  # pour flash et sessions

BACKEND_URL = "http://backend:3000"


def calculate_entropy(password: str) -> float:
    charset_size = 0
    if any(c.islower() for c in password):
        charset_size += 26
    if any(c.isupper() for c in password):
        charset_size += 26
    if any(c.isdigit() for c in password):
        charset_size += 10
    if any(c in string.punctuation for c in password):
        charset_size += 32
    return len(password) * math.log2(charset_size or 1)

@app.route("/login", methods=["GET", "POST"])
def login():
    entropy = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        entropy = calculate_entropy(password)

        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json={"username": username, "password": password},
                timeout=5
            )

            try:
                data = response.json()
            except ValueError:
                data = {}

            if response.status_code == 200 and data:
                session["user"] = {
                    "id": data.get("id"),
                    "username": data.get("username"),
                    "role": data.get("role"),
                    "token": data.get("token")
                }
                return redirect(url_for("dashboard"))
            else:
                flash(data.get("error", response.text or "Erreur inconnue"), "login_error")

        except requests.exceptions.RequestException as e:
            flash(f"Erreur serveur: {str(e)}", "login_error")

    return render_template("login.html", entropy=entropy)


@app.route("/", methods=["GET", "POST"])
def register():
    entropy = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        entropy = calculate_entropy(password)

        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/register",
                json={"username": username, "password": password},
                timeout=5
            )

            try:
                data = response.json()
            except ValueError:
                data = {}

            if response.status_code == 201 and data:
                    flash("Compte créé avec succès ! Connectez-vous.", "register_success")
                    return redirect(url_for("login"))
            else:
                if data.get("error") == "Password leaked in a previous data breach.":
                    flash("Ce mot de passe est trop courant et a déjà fuité : préférez un mot de passe unique", "register_error")
                elif data.get("error") == "Password too redundant (predictable, not varied enough).":
                    flash(data.get("error", response.text or "Erreur inconnue"), "register_error")
                else:
                    flash(data.get("error", response.text or "Erreur inconnue"), "register_error")

        except requests.exceptions.RequestException as e:
            flash(f"Erreur serveur: {str(e)}", "register_error")

    return render_template("register.html", entropy=entropy)


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        flash("Vous devez être connecté pour accéder au dashboard", "login_error")
        return redirect(url_for("login"))

    user = session["user"]
    return render_template("dashboard.html", user=user)


@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Déconnecté avec succès", "login_error")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
