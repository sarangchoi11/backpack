import streamlit as st
import requests
import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")  # Load environment variables from .env


# PostgreSQL 연결 설정
def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")

    )

# 알라딘 Open API에서 책 정보 가져오기
def fetch_book_data(query):
    api_url = "http://www.aladin.co.kr/ttb/api/ItemSearch.aspx"
    params = {
        "ttbkey": os.getenv("ALADIN_API_KEY"),  # 알라딘 API 키
        "Query": query,
        "QueryType": "Title",
        "MaxResults": 10,
        "start": 1,
        "SearchTarget": "Book",
        "output": "js",
        "Version": "20131101"
    }
    response = requests.get(api_url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        return None

# 책 데이터베이스에 등록
def get_next_book_id():
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT MAX(id) FROM books")
    max_id = cur.fetchone()[0]
    
    cur.close()
    conn.close()
    
    return (max_id or 0) + 1

def is_book_already_registered(isbn):
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM books WHERE isbn = %s", (isbn,))
    count = cur.fetchone()[0]
    
    cur.close()
    conn.close()
    
    return count > 0

def register_book_to_db(book_info):
    if is_book_already_registered(book_info['isbn13']):
        return None  # 이미 등록된 책이면 None 반환

    conn = get_connection()
    cur = conn.cursor()

    next_id = get_next_book_id()

    # 책 정보를 데이터베이스에 삽입
    cur.execute("""
        INSERT INTO books (id, isbn, title, author, publisher, genre, category, page_num, cover)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        next_id,
        book_info['isbn13'], 
        book_info['title'], 
        book_info['author'], 
        book_info['publisher'], 
        book_info['categoryName'], 
        book_info['categoryName'], 
        book_info['page_num'], 
        book_info['cover']
    ))

    conn.commit()
    cur.close()
    conn.close()

    return next_id

def get_all_books():
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id, isbn, title, author, publisher, genre, category, page_num, cover FROM books ORDER BY id ASC")
    books = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return books

def register_user_book(book_id, status):
    conn = get_connection()
    cur = conn.cursor()

    # 상태를 정수로 변환
    status_map = {"읽을 예정": 0, "읽는 중": 1, "읽기 완료": 2}
    status_int = status_map[status]

    cur.execute("""
        INSERT INTO user_books (user_id, book_id, status)
        VALUES (%s, %s, %s)
    """, (1, book_id, status_int))

    conn.commit()
    cur.close()
    conn.close()

# Streamlit 화면 구성
def main():
    st.title("📚책 등록 페이지📚")

    if 'search_performed' not in st.session_state:
        st.session_state.search_performed = False
    if 'selected_book' not in st.session_state:
        st.session_state.selected_book = None
    if 'book_data' not in st.session_state:
        st.session_state.book_data = None

    query = st.text_input("책 제목을 입력하세요")
    search_clicked = st.button("책 검색🔍")

    if search_clicked and query:
        book_data = fetch_book_data(query)
        if book_data and 'item' in book_data:
            st.session_state.book_data = book_data
            st.session_state.search_performed = True
        else:
            st.error("책 정보를 불러올 수 없습니다.")
    elif search_clicked:
        st.warning("책 제목을 입력해주세요.")

    if st.session_state.search_performed:
        books_list = []
        for item in st.session_state.book_data['item']:
            books_list.append({
                '제목': item['title'],
                '저자': item['author'],
                '출판사': item['publisher'],
                'ISBN': item['isbn13'],
                '페이지 수': item.get('subInfo', {}).get('itemPage', 'N/A')
            })
        
        df = pd.DataFrame(books_list)
        df.index = range(1, len(df) + 1)
        st.table(df[['제목', '저자', '출판사', 'ISBN', '페이지 수']])

        selected_book_option = st.selectbox("등록할 책을 선택하세요", df.index, key='book_select')
        st.session_state.selected_book = selected_book_option
        reading_status = st.selectbox("읽기 상태를 선택하세요", ["읽을 예정", "읽는 중", "읽기 완료"])

        if st.button("등록📥"):
            if st.session_state.selected_book:
                selected_index = st.session_state.selected_book - 1
                chosen_item = st.session_state.book_data['item'][selected_index]

                book_info = {
                    'isbn13': chosen_item['isbn13'],
                    'title': chosen_item['title'],
                    'author': chosen_item['author'],
                    'publisher': chosen_item['publisher'],
                    'categoryName': chosen_item.get('categoryName', ''),
                    'page_num': int(chosen_item.get('subInfo', {}).get('itemPage', 0)),
                    'cover': chosen_item['cover']
                }
                try:
                    new_book_id = register_book_to_db(book_info)
                    if new_book_id is None:
                        st.warning(f"'{chosen_item['title']}'은(는) 이미 등록된 책입니다.")
                    else:
                        register_user_book(new_book_id, reading_status)
                        st.success(f"'{chosen_item['title']}'이(가) ID {new_book_id}로 등록되었습니다.")
                        st.session_state.book_registered = True  # 책 등록 완료 상태로 설정
                    
                    st.session_state.search_performed = False
                    st.session_state.selected_book = None
                    st.session_state.book_data = None
                except Exception as e:
                    st.error(f"등록 중 오류가 발생했습니다: {e}")
                    st.error(f"Book info: {book_info}")  # 디버깅을 위해 book_info 출력

            st.subheader("등록된 책 보기👀")
            books = get_all_books()
            if books:
                columns = ['ID', 'ISBN', '제목', '저자', '출판사', '장르', '카테고리', '페이지 수', 'none']
                books_df = pd.DataFrame(books, columns=columns)
                
                books_df.set_index('ID', inplace=True)
                display_columns = ['제목', '저자', '출판사', 'ISBN', '페이지 수']
                st.dataframe(books_df[display_columns])
            else:
                st.info("등록된 책이 없습니다.")

if __name__ == "__main__":
    main()


