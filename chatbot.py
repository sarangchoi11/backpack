

import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
import os
from dotenv import load_dotenv

load_dotenv(key_path=".env")

# OpenAI API 키 설정
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# 세션 상태에 메시지 기록 초기화
if 'messages' not in st.session_state:
    st.session_state.messages = [
        SystemMessage(content="You are a helpful assistant.")
    ]
    st.session_state.book_selected = False

st.title("책가방 AI 챗봇")

# ChatOpenAI 객체 생성
chat = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

# 저장된 메시지 표시
for message in st.session_state.messages[1:]:  # SystemMessage 제외
    with st.chat_message("user" if isinstance(message, HumanMessage) else "assistant"):
        st.markdown(message.content)

# 사용자 입력 처리
if prompt := st.chat_input("무엇을 도와드릴까요?"):
    # 사용자 메시지를 기록에 추가
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    # 챗봇 응답 생성
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in chat.stream(st.session_state.messages):
            full_response += response.content
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    
    # 챗봇 응답을 기록에 추가
    st.session_state.messages.append(AIMessage(content=full_response))

# JavaScript 코드
st.markdown("""
<script>
document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        document.querySelector('button.stButton').click();
    }
});
</script>
""", unsafe_allow_html=True)

