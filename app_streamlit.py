import streamlit as st
import json, sqlite3, difflib

# ---------------- Page Config ----------------
st.set_page_config(page_title="Support Assistant", page_icon="💖", layout="centered")

# ---------------- CSS Style ----------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #ff9ecb, #ff6fb1);
    font-family: Arial, sans-serif;
}

.chat-container {
    width: 460px;
    margin: auto;
    background: white;
    border-radius: 18px;
    padding: 20px;
    box-shadow: 0px 0px 20px rgba(0,0,0,0.2);
}

h2 {
    text-align: center;
    margin-bottom: 10px;
    color: #e6007e;
}

#chat-box {
    height: 350px;
    overflow-y: auto;
    border-radius: 12px;
    padding: 12px;
    background: #ffe6f3;
}

.user-msg, .bot-msg {
    padding: 12px;
    margin: 8px 0;
    max-width: 85%;
    border-radius: 18px;
    color: white;
    font-size: 15px;
}

.user-msg {
    background: #ff3c99;
    margin-left: auto;
    border-bottom-right-radius: 2px;
}

.bot-msg {
    background: #b40069;
    border-bottom-left-radius: 2px;
}

.input-area {
    margin-top: 12px;
    display: flex;
    gap: 10px;
}

input, .stTextInput>div>div>input {
    flex: 1;
    padding: 12px;
    border-radius: 14px;
    border: 2px solid #ff7dbd;
    font-size: 15px;
}

button, .stButton>button {
    padding: 12px 22px;
    background: #ff007f;
    color: white;
    border-radius: 14px;
    border: none;
    font-size: 15px;
    cursor: pointer;
}

button:hover, .stButton>button:hover {
    background: #d6006f;
}

.suggestions {
    background: white;
    max-height: 140px;
    overflow-y: auto;
    border-radius: 10px;
    margin-top: 5px;
    box-shadow: 0px 0px 8px rgba(0,0,0,0.2);
}

.suggest-item {
    padding: 8px 12px;
    cursor: pointer;
    border-bottom: 1px solid #ffd6eb;
}

.suggest-item:hover {
    background: #ffe2f3;
}

/* Admin Table */
table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 15px;
}

th, td {
    padding: 12px;
    text-align: center;
    border: 1px solid #ff7cb5;
}

th {
    background: #ffdcf2;
    color: #b81f6e;
}

.status-open {
    color: #d63384;
    font-weight: bold;
}

.status-closed {
    color: #2b9e4d;
    font-weight: bold;
}

.button-close {
    text-decoration: none;
    background: #d63384;
    color: white;
    padding: 6px 14px;
    border-radius: 10px;
}

.button-close:hover {
    background: #b81f6e;
}
</style>
""", unsafe_allow_html=True)

# ---------------- DB Setup ----------------
conn = sqlite3.connect("database.db", check_same_thread=False)
conn.execute("""
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT,
    status TEXT
)
""")
conn.commit()

# ---------------- Helper Functions ----------------
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
    conn.execute("INSERT INTO tickets (query, status) VALUES (?, ?)", (query, "open"))
    conn.commit()

def get_suggestions(text):
    with open("faqs.json", "r") as f:
        faqs = json.load(f)
    return [q["question"] for q in faqs if text.lower() in q["question"].lower()][:7]

# ---------------- Sidebar Navigation ----------------
page = st.sidebar.selectbox("Choose Page", ["Chat", "Admin Panel"])

# ---------------- Chat Page ----------------
if page == "Chat":
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    st.markdown("<h2>💖 Support Assistant</h2>", unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"<div class='user-msg'>{msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot-msg'>{msg['content']}</div>", unsafe_allow_html=True)

    # Input area
    user_input = st.text_input("", key="input", placeholder="Type your message...")

    # Auto-suggestions
    if user_input:
        suggestions = get_suggestions(user_input)
        for s in suggestions:
            if st.button(s):
                user_input = s

    if st.button("Send") and user_input.strip() != "":
        st.session_state.messages.append({"role": "user", "content": user_input})
        answer = get_faq_answer(user_input)
        if answer:
            st.session_state.messages.append({"role": "bot", "content": answer})
        else:
            create_ticket(user_input)
            st.session_state.messages.append({"role": "bot", "content": "Thank you! Your issue has been converted to a ticket. Our support team will contact you."})
        st.experimental_rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Admin Panel ----------------
elif page == "Admin Panel":
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    st.markdown("<h2>📌 Admin — Tickets Panel</h2>", unsafe_allow_html=True)

    tickets = conn.execute("SELECT * FROM tickets").fetchall()
    if tickets:
        st.markdown("<table>", unsafe_allow_html=True)
        st.markdown("<tr><th>ID</th><th>Query</th><th>Status</th><th>Action</th></tr>", unsafe_allow_html=True)
        for t in tickets:
            status_label = f"<span class='status-open'>🟢 Open</span>" if t[2]=="open" else f"<span class='status-closed'>🔴 Closed</span>"
            action = f"<a class='button-close' href='#{t[0]}'>Close</a>" if t[2]=="open" else "—"
            st.markdown(f"<tr><td>{t[0]}</td><td>{t[1]}</td><td>{status_label}</td><td>{action}</td></tr>", unsafe_allow_html=True)
        st.markdown("</table>", unsafe_allow_html=True)
        
        # Close ticket buttons
        for t in tickets:
            if t[2] == "open":
                if st.button(f"Close Ticket {t[0]}"):
                    conn.execute("UPDATE tickets SET status=? WHERE id=?", ("closed", t[0]))
                    conn.commit()
                    st.experimental_rerun()
    else:
        st.info("No tickets yet.")
    st.markdown('</div>', unsafe_allow_html=True)
