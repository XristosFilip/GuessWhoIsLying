from flask import Flask, render_template, request, redirect, url_for, session
import random
from categories import categories

app = Flask(__name__)
app.secret_key = 'super-secret-key'  # Change for production

GAME = {
    "players": [],
    "roles": {},
    "category": "",
    "word": "",
    "started": False
}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name or name in [p["name"] for p in GAME["players"]]:
            return render_template("index.html", error="Please enter a unique name.")
        session["name"] = name
        GAME["players"].append({"name": name})
        return redirect(url_for("lobby"))
    return render_template("index.html", error=None)

@app.route("/lobby")
def lobby():
    name = session.get("name")
    if not name:
        return redirect(url_for("index"))
    return render_template("lobby.html", players=GAME["players"], me=name, started=GAME["started"])

@app.route("/start")
def start():
    if GAME["started"]:
        return redirect(url_for("info"))
    players = GAME["players"]
    if len(players) < 2:
        return redirect(url_for("lobby"))
    imposter_index = random.randint(0, len(players)-1)
    category = random.choice(list(categories.keys()))
    word = random.choice(categories[category])
    GAME["category"] = category
    GAME["word"] = word
    GAME["roles"] = {}
    for i, p in enumerate(players):
        GAME["roles"][p["name"]] = "Imposter" if i == imposter_index else "Investigator"
    GAME["started"] = True
    return redirect(url_for("info"))

@app.route("/info")
def info():
    name = session.get("name")
    if not name or name not in GAME["roles"]:
        return redirect(url_for("index"))
    role = GAME["roles"][name]
    category = GAME["category"]
    word = GAME["word"] if role == "Investigator" else None
    return render_template("info.html", name=name, role=role, category=category, word=word)

@app.route("/reset")
def reset():
    # Only reset the game state, not the players
    GAME["roles"] = {}
    GAME["category"] = ""
    GAME["word"] = ""
    GAME["started"] = False
    return redirect(url_for("lobby"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)