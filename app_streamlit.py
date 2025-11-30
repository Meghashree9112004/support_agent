import streamlit as st
import json, sqlite3, difflib

# ----------------- Page config -----------------
st.set_page_config(page_title="Support Assistant", page_icon="💖", layout="centered")

# ----------------- Custom CSS for pink chat UI -----------------
st.markdown("""
<style>
body {
    background: #ff80b3;
}
.chat-container {
    background: #ffe6f3;
    border-radius: 20px;
    padding: 20px;
    width: 500px;
    margin: auto;
}
.user-msg {
    background: #ff3c99;
    color: white;
    padding: 10px;
    border-radius: 15px;
    margin: 5px 0;
    text-align: right;
}
.bot-msg {
    background: #b40069;
    color: white;
    padding: 10px;
    border-radius: 15px;
    margin: 5px 0;
    text-align: left;
}
input {
    padding: 10px;
    width: 80%;
    border-radius: 10px;
    border: 2px solid #ff7cb5;
}
button {
    padding: 10px 20px;
    background: #ff007f;
    color: white;
    border: none;
    border-radius: 10px;
    cursor: pointer;
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

# ----------------- Session state for messages -----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------- Main UI -----------------
st.markdown("<h2 style='text-align:center;color:#e6007e'>💖 Support Assistant</h2>", unsafe_allow_html=True)

chat_box = st.container()
with chat_box:
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for sender, msg in st.session_state.messages:
        if sender == "user":
            st.markdown(f"<div class='user-msg'>{msg}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot-msg'>{msg}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- Input and send -----------------
user_input = st.text_input("", placeholder="Type your message...", key="input")

if st.button("Send"):
    if user_input.strip() != "":
        # Add user message
        st.session_state.messages.append(("user", user_input))

        # Get bot answer
        answer = get_faq_answer(user_input)
        if answer:
            st.session_state.messages.append(("bot", answer))
        else:
            create_ticket(user_input)
            st.session_state.messages.append(("bot", "Thank you! Your issue has been converted to a ticket. Our support team will contact you."))

        # Clear input and refresh chat
        st.session_state.input = ""
        st.experimental_rerun()
