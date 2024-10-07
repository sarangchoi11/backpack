import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv
import csv
from datetime import datetime
from collections import defaultdict
import pandas as pd

load_dotenv('.env')
st.title("Memo 📝")

# Initialize memos.csv file if it doesn't exist
def initialize_csv(filename, headers):
    if not os.path.exists(filename):
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)

def save_memo(filename, book_title, content):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['', '', book_title, content, current_time, current_time])

def load_book_titles(books_csv):
    df = pd.read_csv(books_csv)
    return df['title'].tolist()

def load_memos(memo_filename):
    if os.path.exists(memo_filename):
        return pd.read_csv(memo_filename)
    return pd.DataFrame(columns=['id', 'user_id', 'book_id', 'content', 'created_at', 'updated_at'])

def save_and_clear_memo():
    if st.session_state.memo_input and st.session_state.selected_book:
        save_memo(memo_filename, st.session_state.selected_book, st.session_state.memo_input)
        st.session_state.memo_input = ""
        st.success("메모가 저장되었습니다.", icon="✅")
    else:
        st.warning("메모를 작성해주세요.", icon="🚨")

# Initialize the memos.csv file
memo_filename = 'memos.csv'
memo_headers = ['id', 'user_id', 'book_id', 'content', 'created_at', 'updated_at']
initialize_csv(memo_filename, memo_headers) 

# Prevent from overwriting the csv file every time the code is executed
if not os.path.exists('books.csv'):
    df = pd.read_excel('books.xlsx', sheet_name='Sheet1')
    df.to_csv('books.csv', index=False)
else:
    df = pd.read_csv('books.csv')

# Load book titles
book_titles = load_book_titles('books.csv')

# Load past memos
memos_df = load_memos('memos.csv')

# Get the 5 most recent books with memos
memos_df['created_at'] = pd.to_datetime(memos_df['created_at'])
recent_books = memos_df.sort_values('created_at', ascending=False)['book_id'].unique()[:5]
selectbox_options = ['모든 책'] + list(recent_books)

# Book selection
book_select = st.selectbox("어떤 책을 위한 메모인가요?", book_titles, key="selected_book")

# Memo input using session state
if "memo_input" not in st.session_state:
    st.session_state.memo_input = ""

# Memo input
memo_input = st.text_area("Memo", key="memo_input", value=st.session_state.memo_input)

# Save the memo
st.button("메모 저장", on_click=save_and_clear_memo)

# Save the memo in the DB
# if st.button("Save"):
#     if memo_input and book_select:
#         save_memo(memo_filename, book_select, memo_input)
#         st.success("메모가 저장되었어요!")

#         st.session_state[memo_key] = ""

#         memos_df = load_memos('memos.csv')

#         st.rerun()

#     else:
#         st.warning("메모를 적어주세요.")

# Display saved memos
st.subheader("저장된 메모 보기 🗃️")

selected_book_for_display = st.selectbox("어떤 책의 메모를 보시겠습니까?", selectbox_options)

if selected_book_for_display == '모든 책':
    display_memos = memos_df
else:
    display_memos = memos_df[memos_df['book_id'] == selected_book_for_display]

if not display_memos.empty:
    for _, memo in display_memos.iterrows():
        #st.text(f"책 제목: {memo['book_id']}")
        st.text(f"메모 내용: {memo['content']}")
        st.text(f"작성 시간: {memo['created_at']}")
        st.text("---")
else:
    st.info("선택한 책에 대한 메모가 없습니다.")

