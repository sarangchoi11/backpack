import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv
import csv
from datetime import datetime
from collections import defaultdict

load_dotenv('.env')
st.title("Memo 📝")

# function to read csv files
def read_csv(filename):
    data = {}
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data[row['id']] = row

    return data

# read the csv files
books = read_csv('books.csv')
notes = read_csv('notes.csv')

# memo header
#header = ['id', 'user_id', 'book_id', 'book_title', 'book_author', 'content', 'created_at', 'updated_at'] # sample
#sample_data = []

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

#book_choices = ["book1", "book2", "book3"] # later, get titles from db
book_title_index = header.index('book_title')
book_title_column = [row[book_title_index] for row in sample_data]
book_select = st.selectbox("어떤 책을 위한 메모인가요?", book_title_column)

memo_input = st.text_area("Memo")

if st.button("Save"):
    st.write(memo_input)

# save memo in the db


