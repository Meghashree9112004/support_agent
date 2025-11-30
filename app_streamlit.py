import streamlit as st
import json
import sqlite3
import difflib

st.set_page_config(page_title="AI Support Assistant", page_icon="💖", layout="centered")

# Load FAQs
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

# Create ticket if no matching FAQ
def create_ticket(query):
    conn = sqlite3.connect("database.db")
    conn.execute("INSERT INTO tickets (query, status) VALUES (?, ?)", (query, "open"))
    conn.commit()
    conn.close()

st.title("💖 AI Support Assistant")
st.write("Ask your queries anytime — I will assist you.")

# Chat Input
user_input = st.text_input("Type your message:")

if st.button("Send"):
    if user_input.strip() != "":
        answer = get_faq_answer(user_input)

        if answer:
            st.success("🤖 " + answer)
        else:
            create_ticket(user_input)
            st.warning("🎫 Your query has been converted into a ticket. Our support team will contact you soon.")

# Admin Section
with st.expander("Admin Panel"):
    conn = sqlite3.connect("database.db")
    tickets = conn.execute("SELECT * FROM tickets").fetchall()
    conn.close()

    if tickets:
        for t in tickets:
            st.write(f"🆔 Ticket ID: {t[0]}")
            st.write(f"📌 Query: {t[1]}")
            st.write(f"🔖 Status: {t[2]}")
            st.write("---")
    else:
        st.write("No tickets yet.")
