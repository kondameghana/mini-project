from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__)

# 📁 Upload folder
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# 🧠 Label Extraction Function
def extract_labels(text):

    keywords = [
        "fracture",
        "tumor",
        "infection",
        "lesion",
        "opacity",
        "nodule",
        "pneumonia",
        "effusion",
        "consolidation"
    ]

    labels = []

    for word in keywords:
        if word in text.lower():
            labels.append(word)

    return labels


# 🏠 HOME
@app.route("/")
def home():
    return render_template("index.html")


# 📤 UPLOAD
@app.route("/upload", methods=["GET", "POST"])
def upload():

    extracted = []
    report_text = ""

    if request.method == "POST":

        file = request.files.get("report")

        # ✅ Only allow txt files
        if file and file.filename.endswith(".txt"):

            path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(path)

            try:
                with open(path, "r", encoding="utf-8") as f:
                    report_text = f.read()
            except:
                report_text = "Error reading file"

            extracted = extract_labels(report_text)

            # 💾 Database
            conn = sqlite3.connect("database.db")
            c = conn.cursor()

            c.execute("CREATE TABLE IF NOT EXISTS results (report TEXT, labels TEXT)")

            c.execute("INSERT INTO results VALUES (?, ?)",
                      (report_text, ", ".join(extracted)))

            conn.commit()
            conn.close()

        else:
            report_text = "Please upload a valid .txt file"

    return render_template("upload.html",
                           report=report_text,
                           labels=extracted)


# 📊 ADMIN
@app.route("/admin")
def admin():

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS results (report TEXT, labels TEXT)")
    c.execute("SELECT labels FROM results")

    data = c.fetchall()
    conn.close()

    # Count labels
    label_count = {}

    for row in data:
        labels = row[0].split(", ")
        for label in labels:
            if label:
                label_count[label] = label_count.get(label, 0) + 1

    return render_template("admin.html",
                           chart_data=label_count,
                           records=data)


# ℹ️ ABOUT
@app.route("/about")
def about():
    return render_template("about.html")


# 🚀 RUN
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
