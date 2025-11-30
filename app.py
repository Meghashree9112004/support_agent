from flask import Flask, render_template, request, jsonify
import json, sqlite3, difflib



app = Flask(__name__)

def get_faq_answer(user_msg):
    with open("faqs.json", "r") as f:
        faqs = json.load(f)
    questions = [faq["question"] for faq in faqs]
    match = difflib.get_close_matches(user_msg, questions, n=1, cutoff=0.6)
    if match:
        for faq in faqs:
            if faq["question"] == match[0]:
                return faq["answer"]
    return None

def create_ticket(query):
    conn = sqlite3.connect("database.db")
    conn.execute("INSERT INTO tickets (query, status) VALUES (?, ?)", (query, "open"))
    conn.commit()
    conn.close()

@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/admin")
def admin():
    conn = sqlite3.connect("database.db")
    tickets = conn.execute("SELECT * FROM tickets").fetchall()
    conn.close()
    return render_template("admin.html", tickets=tickets)

@app.route("/close_ticket/<int:id>")
def close_ticket(id):
    conn = sqlite3.connect("database.db")
    conn.execute("UPDATE tickets SET status=? WHERE id=?", ("closed", id))
    conn.commit()
    conn.close()
    return "Ticket Closed <a href='/admin'>Back</a>"

# 🔥 Auto suggestion API added (NEW)
@app.route("/suggest")
def suggest():
    text = request.args.get("text", "").lower()
    with open("faqs.json", "r") as f:
        faqs = json.load(f)
    matches = [q["question"] for q in faqs if text in q["question"].lower()]
    return jsonify(matches[:7])

@app.route("/chat", methods=["POST"])
def chat():
    msg = request.form["message"]
    answer = get_faq_answer(msg)

    if answer:
        return jsonify({"reply": answer})
    else:
        create_ticket(msg)
        return jsonify({"reply": "Thank you! Your issue has been converted to a ticket. Our support team will contact you."})

if __name__ == "__main__":
    app.run(debug=True)
