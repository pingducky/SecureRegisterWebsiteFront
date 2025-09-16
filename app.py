from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "secret123"  # nécessaire pour les messages flash

# Utilisateurs fictifs
users = {
    "admin": "password123",
    "user": "pass"
}

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in users and users[username] == password:
            return f"Bienvenue, {username} !"
        else:
            flash("Nom d'utilisateur ou mot de passe incorrect")
            return redirect(url_for("login"))

    return render_template("login.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
