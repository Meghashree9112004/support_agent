import streamlit as st
import json, sqlite3, difflib

# -------------- Page Config ----------------
st.set_page_config(page_title="Support Assistant", page_icon="💖", layout="centered")

# -------------- Custom CSS (Pink Theme) ----------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #ff9ecb, #ff6fb1);
}
.chat-box {
    height: 380px;
    overflow-y: auto;
    padding: 12px;
    border-radius: 12px;
    background: #ffe6f3;
    box-shadow: 0px 0px 8px rgba(0,0,0,0.25);
}
.user-msg {
    background: #ff3c99;
    color: white;
    padding: 12px;
    margin: 8px 0;
    margin-left: auto;
    max-width: 75%;
    border-radius: 18px;
}
.bot-msg {
    background: #b40069;
    color: white;
    padding: 12px;
    margin: 8px 0;
    max-width: 75%;
    border-radius: 18px;
}
.suggest-box {
    background: white;
    max-height: 140px;
    overflow-y: auto;
    border-radius: 12px;
    box-shadow: 0 0 8px rgba(0,0,0,0.2);
}
.suggest-item {
    padding: 10px;
    cursor: pointer;
}
.suggest-item:hover {
    background: #ffe2f3;
}
</style>
""", unsafe_allow_html=True)


# ----------------- Helper functions -----------------
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

def get_suggestions(text):
    with open("faqs.json", "r") as f:
        faqs = json.load(f)
    return [q["question"] for q in faqs if text.lower() in q["question"].lower()]


# ----------------- Chat Memory -----------------
if "messages" not in st.session_state:
    st.session_state.messages = []


# ----------------- Main UI -----------------
st.title("💖 Support Assistant")

# Chat Box
chat = st.container()
with chat:
    st.markdown("<div class='chat-box'>", unsafe_allow_html=True)
    for sender, msg in st.session_state.messages:
        if sender == "user":
            st.markdown(f"<div class='user-msg'>{msg}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot-msg'>{msg}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Input box
user_input = st.text_input("Type your message…", key="input", placeholder="Type something...")

# Suggestions box
if user_input and len(user_input) >= 2:
    suggestions = get_suggestions(user_input)
    if suggestions:
        st.markdown("<div class='suggest-box'>", unsafe_allow_html=True)
        for s in suggestions[:7]:
            if st.button(s):
                st.session_state.input = s
                user_input = s
        st.markdown("</div>", unsafe_allow_html=True)

# Send message
if st.button("Send"):
    if user_input.strip() != "":
        st.session_state.messages.append(("user", user_input))
        answer = get_faq_answer(user_input)
        if answer:
            st.session_state.messages.append(("bot", answer))
        else:
            create_ticket(user_input)
            st.session_state.messages.append(("bot", "Thank you! Your issue has been converted to a ticket. Our support team will contact you."))
        st.rerun()


# ----------------- Admin Panel Button ----------------
if st.sidebar.button("🔐 Open Admin Panel"):
    st.session_state["admin_mode"] = True

# ----------------- Admin Panel ----------------
if st.session_state.get("admin_mode", False):
    st.header("📌 Admin — Support Tickets Panel")
    conn = sqlite3.connect("database.db")
    data = conn.execute("SELECT * FROM tickets").fetchall()

    for t in data:
        col1, col2, col3, col4 = st.columns([1, 5, 2, 2])
        col1.write(t[0])
        col2.write(t[1])
        col3.write(t[2])

        if t[2] == "open":
            if col4.button("Close", key=f"close_{t[0]}"):
                conn.execute("UPDATE tickets SET status=? WHERE id=?", ("closed", t[0]))
                conn.commit()
                st.rerun()
        else:
            col4.write("Closed")

    conn.close()
