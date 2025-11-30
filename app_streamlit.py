import streamlit as st
import json
import difflib

# Load FAQ questions
with open("faqs.json", "r") as f:
    faqs = json.load(f)
questions = [faq["question"] for faq in faqs]

st.markdown("""
<style>
body {background-color: #ffb3d9;}
.chat-box {
    background-color: #ffe6f2;
    padding: 20px;
    border-radius: 20px;
    height: 400px;
}
.input-box {
    width: 100%;
    padding: 12px;
    border-radius: 10px;
    border: 2px solid #ff4da6;
}
.send-btn {
    background-color: #ff027c;
    color: white;
    padding: 10px 20px;
    border-radius: 10px;
    border: none;
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

st.title("💖 Support Assistant")
st.write('<div class="chat-box"></div>', unsafe_allow_html=True)

user_msg = st.text_input("Type your message...", key="msg", placeholder="Ask anything")

# Auto suggestions
if user_msg:
    matches = difflib.get_close_matches(user_msg, questions, n=5, cutoff=0.2)
    if matches:
        selected = st.selectbox("Suggested questions:", matches)
    else:
        selected = None
else:
    selected = None

if st.button("Send"):
    query = selected if selected else user_msg
    matched = difflib.get_close_matches(query, questions, n=1, cutoff=0.6)

    if matched:
        for faq in faqs:
            if faq["question"] == matched[0]:
                st.success("💡 Answer: " + faq["answer"])
    else:
        st.error("❗ No answer found. Ticket created for support team.")
