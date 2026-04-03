from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# simple label extraction function
def extract_labels(text):

    labels = []

    keywords = [
        "fracture",
        "tumor",
        "infection",
        "lesion",
        "opacity",
        "nodule"
    ]

    for word in keywords:
        if word in text.lower():
            labels.append(word)

    return labels


# Home Page
@app.route("/")
def home():
    return render_template("index.html")


# Upload Page
@app.route("/upload", methods=["GET","POST"])
def upload():

    extracted = []
    report_text = ""

    if request.method == "POST":

        file = request.files["report"]

        if file:

            path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(path)

            with open(path,"r") as f:
                report_text = f.read()

            extracted = extract_labels(report_text)

            conn = sqlite3.connect("database.db")
            c = conn.cursor()

            c.execute("INSERT INTO results VALUES (?,?)",
                      (report_text,", ".join(extracted)))

            conn.commit()
            conn.close()

    return render_template("upload.html",
                           report=report_text,
                           labels=extracted)


# Admin Dashboard
@app.route("/admin")
def admin():

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT * FROM results")
    records = c.fetchall()

    conn.close()

    return render_template("admin.html", records=records)


# About Page
@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)