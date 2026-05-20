"""Streamlit 챗봇 UI — AI 데이터 분석가."""
from __future__ import annotations

from typing import Optional

import streamlit as st

from bedrock_client import ask_text2sql
from data_executor import run_query, validate_select_only
from query_parser import build_prompt
from visualizer import generate_chart, generate_description


def main() -> None:
    """Streamlit 앱 진입점."""
    st.set_page_config(page_title="AI 데이터 분석가", page_icon="📊", layout="wide")
    st.title("📊 AI 데이터 분석가")
    st.caption("자연어로 데이터에 대해 질문하세요. AI가 분석하고 시각화합니다.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    _render_history()
    _handle_input()


def _render_history() -> None:
    """대화 히스토리를 렌더링한다."""
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "image" in msg and msg["image"] is not None:
                st.image(msg["image"], use_container_width=True)
            if "dataframe" in msg:
                st.dataframe(msg["dataframe"], use_container_width=True)


def _handle_input() -> None:
    """사용자 입력을 처리한다."""
    question = st.chat_input("데이터에 대해 궁금한 점을 물어보세요...")
    if not question:
        return

    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # 어시스턴트 응답
    with st.chat_message("assistant"):
        with st.spinner("분석 중..."):
            _run_pipeline(question)


def _run_pipeline(question: str) -> None:
    """3-모델 파이프라인을 실행하고 결과를 렌더링한다."""
    # Step 1: 프롬프트 조립 + Text2SQL (Model-1)
    try:
        prompt = build_prompt(question)
        result = ask_text2sql(question, prompt)
        sql = result.get("sql", "")
        st.info(f"🔍 생성된 SQL: `{sql}`")
    except Exception as e:
        _show_error(f"SQL 생성에 실패했습니다: {e}")
        return

    # Step 2: SQL 검증 + Athena 실행
    try:
        validate_select_only(sql)
        df = run_query(sql)
        st.info(f"✅ Athena 성공: {len(df)}행 반환")
    except ValueError as e:
        _show_error(str(e))
        return
    except RuntimeError as e:
        _show_error(f"쿼리 실행에 실패했습니다: {e}")
        return
    except Exception as e:
        _show_error(f"데이터 조회 중 오류가 발생했습니다: {e}")
        return

    # Step 3: 차트 생성 (Model-2) — 실패해도 계속 진행
    try:
        chart_image = generate_chart(question, df)
        st.info(f"📊 차트 생성: {'성공' if chart_image else '실패(None)'}")
    except Exception as e:
        st.warning(f"차트 생성 에러: {e}")
        chart_image = None

    # Step 4: 설명 작성 (Model-3) — 실패해도 계속 진행
    try:
        description = generate_description(question, df, chart_image)
    except Exception as e:
        st.warning(f"설명 생성 에러: {e}")
        description = "설명 생성에 실패했습니다."

    # Step 5: 결과 렌더링
    _render_result(description, chart_image, df)


def _render_result(
    description: str, chart_image: Optional[bytes], df: "pd.DataFrame"
) -> None:
    """분석 결과를 Streamlit에 렌더링한다."""
    # 설명 표시
    st.markdown(description)

    # 차트 이미지 표시
    if chart_image:
        st.image(chart_image, use_container_width=True)

    # 데이터 테이블 표시
    with st.expander("📋 데이터 테이블 보기", expanded=False):
        st.dataframe(df, use_container_width=True)

    # 세션에 저장
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": description,
            "image": chart_image,
            "dataframe": df,
        }
    )


def _show_error(message: str) -> None:
    """에러 메시지를 표시한다."""
    st.error(message)
    st.session_state.messages.append({"role": "assistant", "content": f"⚠️ {message}"})


if __name__ == "__main__":
    main()
