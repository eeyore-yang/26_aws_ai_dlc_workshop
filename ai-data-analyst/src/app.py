"""Streamlit 챗봇 UI."""
import os
import streamlit as st
from bedrock_client import ask_bedrock
from data_executor import run_query
from visualizer import build_chart

MOCK_MODE: bool = os.getenv("MOCK_MODE", "false").lower() == "true"

def main() -> None:
    st.set_page_config(page_title="AI 데이터 분석가", page_icon="📊", layout="wide")
    st.title("📊 AI 데이터 분석가")
    if MOCK_MODE:
        st.warning("MOCK_MODE 활성 — Bedrock 미연결 상태입니다.")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    _render_history()
    _handle_input()

def _render_history() -> None:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "figure" in msg:
                st.plotly_chart(msg["figure"], use_container_width=True)
            if "dataframe" in msg:
                st.dataframe(msg["dataframe"], use_container_width=True)

def _handle_input() -> None:
    question = st.chat_input("데이터에 대해 궁금한 점을 물어보세요...")
    if not question:
        return
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        with st.spinner("분석 중..."):
            _run_pipeline(question)

def _run_pipeline(question: str) -> None:
    """Text2SQL 파이프라인 실행 후 결과를 렌더링한다."""
    raise NotImplementedError

if __name__ == "__main__":
    main()
