"""Streamlit 챗봇 UI — AI 데이터 분석가 + 동적 데이터 마트 에이전트."""
from __future__ import annotations

from typing import Optional

import streamlit as st

from bedrock_client import ask_text2sql
from data_executor import run_query, validate_select_only
from mart_agent import run_mart_pipeline
from query_parser import build_prompt
from visualizer import generate_chart, generate_description


def main() -> None:
    """Streamlit 앱 진입점."""
    st.set_page_config(page_title="AI 데이터 분석가", page_icon="📊", layout="wide")
    st.title("📊 AI 데이터 분석가")
    st.caption("자연어로 데이터에 대해 질문하세요. AI가 분석하고 시각화합니다.")

    # 사이드바: 예시 질문
    with st.sidebar:
        st.header("💡 예시 질문")
        st.subheader("단순 분석")
        simple_examples = [
            "제품 유형별 총 매출을 보여줘",
            "월별 매출 추이를 보여줘",
            "성별 구매 비중은?",
            "연령대별 평균 구매 금액은?",
        ]
        for ex in simple_examples:
            if st.button(ex, use_container_width=True, key="s_" + ex[:10]):
                st.session_state["pending_question"] = ex

        st.subheader("🏗️ 데이터 마트 생성")
        mart_examples = [
            "연령대별 제품유형별 월간 매출 마트를 만들어줘",
            "고객 세그먼트별 구매 패턴 분석용 마트 구성해줘",
            "결제수단별 배송유형별 주문 분석 마트를 생성해줘",
        ]
        for ex in mart_examples:
            if st.button(ex, use_container_width=True, key="m_" + ex[:10]):
                st.session_state["pending_question"] = ex

    if "messages" not in st.session_state:
        st.session_state.messages = []

    _render_history()
    _handle_input()


def _render_history() -> None:
    """대화 히스토리를 렌더링한다."""
    for msg in st.session_state.messages:
        role = msg["role"]
        prefix = "🧑 **You:**" if role == "user" else "🤖 **AI:**"
        st.markdown(f"{prefix} {msg['content']}")
        if "image" in msg and msg["image"] is not None:
            st.image(msg["image"], use_container_width=True)
        if "dataframe" in msg:
            st.dataframe(msg["dataframe"], use_container_width=True)
        st.markdown("---")


def _handle_input() -> None:
    """사용자 입력을 처리한다."""
    # 사이드바 버튼에서 온 질문
    question = st.session_state.pop("pending_question", None)

    # 텍스트 입력
    if not question:
        with st.form("question_form", clear_on_submit=True):
            user_input = st.text_input(
                "질문을 입력하세요:",
                placeholder="예: 월별 매출 추이를 보여줘",
            )
            submitted = st.form_submit_button("🚀 분석 시작")
            if submitted and user_input.strip():
                question = user_input.strip()

    if not question:
        return

    # 사용자 메시지 저장
    st.session_state.messages.append({"role": "user", "content": question})
    st.markdown(f"🧑 **You:** {question}")
    st.markdown("---")

    # 의도 분석
    with st.spinner("🤖 의도 분석 중..."):
        try:
            intent_type, context = run_mart_pipeline(question)
        except Exception as e:
            st.warning(f"의도 분류 실패, 기본 분석으로 진행: {e}")
            intent_type = "simple_analysis"
            context = {}

    if intent_type == "mart_creation":
        _run_mart_creation(question, context)
    else:
        with st.spinner("분석 중..."):
            _run_simple_analysis(question)


def _run_simple_analysis(question: str) -> None:
    """기존 3-모델 파이프라인 (단순 분석)."""
    try:
        prompt = build_prompt(question)
        result = ask_text2sql(question, prompt)
        sql = result.get("sql", "")
        st.info(f"🔍 생성된 SQL: `{sql}`")
    except Exception as e:
        _show_error(f"SQL 생성 실패: {e}")
        return

    try:
        validate_select_only(sql)
        df = run_query(sql)
        st.info(f"✅ {len(df)}행 반환")
    except (ValueError, RuntimeError) as e:
        _show_error(str(e))
        return
    except Exception as e:
        _show_error(f"데이터 조회 오류: {e}")
        return

    chart_image = _safe_chart(question, df)
    description = _safe_description(question, df, chart_image)
    _render_result(description, chart_image, df)


def _run_mart_creation(question: str, context: dict) -> None:
    """데이터 마트 생성 → 분석 파이프라인."""
    view_name = context.get("view_name", "")
    mart_description = context.get("mart_description", "")
    mart_sql = context.get("mart_sql", "")
    analysis_prompt = context.get("analysis_prompt", "")

    st.success(f"🏗️ 데이터 마트 생성 완료: `{view_name}`")
    if mart_description:
        st.info(f"📋 {mart_description}")
    with st.expander("🔧 생성된 VIEW SQL", expanded=False):
        st.code(mart_sql, language="sql")

    try:
        result = ask_text2sql(question, analysis_prompt)
        sql = result.get("sql", "")
        st.info(f"🔍 분석 SQL: `{sql}`")
    except Exception as e:
        _show_error(f"마트 분석 SQL 생성 실패: {e}")
        return

    try:
        validate_select_only(sql)
        df = run_query(sql)
        st.info(f"✅ {len(df)}행 반환")
    except (ValueError, RuntimeError) as e:
        _show_error(str(e))
        return
    except Exception as e:
        _show_error(f"데이터 조회 오류: {e}")
        return

    chart_image = _safe_chart(question, df)
    description = _safe_description(question, df, chart_image)
    _render_result(description, chart_image, df)


def _safe_chart(question, df):
    try:
        return generate_chart(question, df)
    except Exception:
        return None


def _safe_description(question, df, chart_image):
    try:
        return generate_description(question, df, chart_image)
    except Exception:
        return "분석 결과입니다."


def _render_result(description, chart_image, df):
    """분석 결과를 렌더링한다."""
    st.markdown(f"🤖 **AI:** {description}")

    if chart_image:
        st.image(chart_image, use_container_width=True)

    with st.expander("📋 데이터 테이블 보기", expanded=False):
        st.dataframe(df, use_container_width=True)

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
