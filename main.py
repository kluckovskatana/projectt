import os

from flask import Flask, render_template, request, redirect, url_for, flash, session
from supabase import create_client
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

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

        action = request.form.get("action")

        name = request.form.get("name", "").strip()
        password = request.form.get("password", "")
        password_confirm = request.form.get("password_confirm", "")

        # -------------------------
        # РЕЄСТРАЦІЯ
        # -------------------------
        if action == "register":

            if not name or not password or not password_confirm:
                flash("Заповніть усі поля")
                return redirect(url_for("login"))

            if password != password_confirm:
                flash("Паролі не збігаються")
                return redirect(url_for("login"))

            if len(password) < 6:
                flash("Пароль повинен містити щонайменше 6 символів")
                return redirect(url_for("login"))

            try:
                # Перевіряємо, чи існує користувач
                result = (
                    supabase
                    .table("users")
                    .select("id")
                    .eq("name", name)
                    .execute()
                )

                if result.data:
                    flash("Користувач з таким ім'ям уже існує")
                    return redirect(url_for("login"))

                # Хешуємо пароль
                hashed_password = generate_password_hash(password)

                # Додаємо користувача в Supabase
                supabase.table("users").insert({
                    "name": name,
                    "password": hashed_password
                }).execute()

                flash("Реєстрація успішна! Тепер увійдіть.")
                return redirect(url_for("login"))

            except Exception as e:
                print("Помилка реєстрації:", e)
                flash("Помилка при реєстрації")

                return redirect(url_for("login"))

        # -------------------------
        # ВХІД
        # -------------------------
        if action == "login":

            if not name or not password:
                flash("Заповніть усі поля")
                return redirect(url_for("login"))

            try:
                # Шукаємо користувача
                result = (
                    supabase
                    .table("users")
                    .select("id, name, password")
                    .eq("name", name)
                    .execute()
                )

                if not result.data:
                    flash("Користувача не знайдено")
                    return redirect(url_for("login"))

                user = result.data[0]

                # Перевіряємо пароль
                if not check_password_hash(user["password"], password):
                    flash("Неправильний пароль")
                    return redirect(url_for("login"))

                # Зберігаємо користувача в сесії
                session["user_id"] = user["id"]
                session["user_name"] = user["name"]

                return redirect(url_for("shop"))

            except Exception as e:
                print("Помилка входу:", e)
                flash("Помилка при вході")

                return redirect(url_for("login"))

    return render_template("index.html")

@app.route("/shop")
def shop():


    try:
        result = (
            supabase
            .table("clothes")
            .select("name, image, price, qnt")
            .execute()
        )

        products = result.data

        return render_template(
            "catalog.html",
            products=products
        )

    except Exception as e:
        print("Помилка:", e)

        flash("Не вдалося завантажити товари")

        return redirect(url_for("login"))

# -------------------------
# ВИХІД
# -------------------------
@app.route("/logout")
def logout():

    session.clear()

    flash("Ви вийшли з акаунта")

    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)