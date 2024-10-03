import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv('.env')

st.title("Memo 📝")

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

book_choices = ["book1", "book2", "book3"] # later, get titles from db
book_select = st.selectbox("어떤 책을 위한 메모인가요?", book_choices)

memo_input = st.text_area("Memo")

if st.button("Save"):
    st.write(memo_input)

# save memo in the db
