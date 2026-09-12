import os

from flask import Flask, render_template, request, redirect, url_for, flash
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "secret-key")

supabase = create_client(
    os.getenv("DB_LINK"),
    os.getenv("DB_KEY")
)


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        password = request.form.get("password", "")

        if not name or not password:
            flash("Заповніть усі поля")
            return redirect(url_for("login"))

        try:
            # Зберігаємо користувача в Supabase
            supabase.table("users").insert({
                "name": name,
                "password": password
            }).execute()

            return render_template(
                "index.html",
                success=f"Вітаємо, {name}!"
            )

        except Exception as e:
            print(e)
            flash("Помилка при збереженні користувача")

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
