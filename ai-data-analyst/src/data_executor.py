"""Amazon Athena SQL 실행 레이어."""
import os
import time

import boto3
import pandas as pd

REGION: str = os.getenv("AWS_DEFAULT_REGION", os.getenv("AWS_REGION", "us-east-1"))
ATHENA_DATABASE: str = os.getenv("ATHENA_DATABASE", "aidlc_workshop")
ATHENA_WORKGROUP: str = os.getenv("ATHENA_WORKGROUP", "primary")
ATHENA_OUTPUT: str = os.getenv(
    "ATHENA_OUTPUT_LOCATION",
    "s3://aidlc-workshop-athena-results-251165958261/query-results/",
)

_client = boto3.client("athena", region_name=REGION)

# SQL 실행 최대 대기 시간 (초)
_MAX_WAIT_SECONDS = 60
_POLL_INTERVAL = 1.0


def validate_select_only(sql: str) -> None:
    """SQL이 SELECT 문인지 검증한다.

    Raises:
        ValueError: SELECT 외 문장이 감지된 경우
    """
    normalized = sql.strip().upper()
    forbidden = ["INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER", "TRUNCATE"]
    for keyword in forbidden:
        if normalized.startswith(keyword):
            raise ValueError(
                f"위험한 SQL이 감지되었습니다: {keyword} 문은 허용되지 않습니다."
            )


def validate_view_ddl(sql: str) -> None:
    """CREATE OR REPLACE VIEW 문만 허용한다.

    Raises:
        ValueError: 허용되지 않는 DDL인 경우
    """
    normalized = sql.strip().upper()
    if not normalized.startswith("CREATE OR REPLACE VIEW"):
        raise ValueError(
            "허용되지 않는 DDL입니다. CREATE OR REPLACE VIEW만 지원합니다."
        )
    # DROP, DELETE 등 위험 키워드가 포함되어 있는지 추가 검증
    dangerous = ["DROP ", "DELETE ", "INSERT ", "UPDATE ", "TRUNCATE "]
    for keyword in dangerous:
        if keyword in normalized:
            raise ValueError(
                f"위험한 키워드가 감지되었습니다: {keyword.strip()}"
            )


def run_ddl(sql: str) -> None:
    """Athena에서 DDL(CREATE OR REPLACE VIEW)을 실행한다.

    Args:
        sql: CREATE OR REPLACE VIEW SQL 문자열

    Raises:
        ValueError: 허용되지 않는 DDL인 경우
        RuntimeError: Athena 실행 실패 시
    """
    validate_view_ddl(sql)

    response = _client.start_query_execution(
        QueryString=sql,
        QueryExecutionContext={"Database": ATHENA_DATABASE},
        WorkGroup=ATHENA_WORKGROUP,
        ResultConfiguration={"OutputLocation": ATHENA_OUTPUT},
    )
    query_execution_id = response["QueryExecutionId"]
    _wait_for_query(query_execution_id)


def run_query(sql: str) -> pd.DataFrame:
    """Athena에서 SQL을 실행하고 결과를 DataFrame으로 반환한다.

    Args:
        sql: SELECT SQL 문자열

    Returns:
        쿼리 결과 pandas DataFrame

    Raises:
        ValueError: SELECT 외 SQL인 경우
        RuntimeError: Athena 실행 실패 시
    """
    validate_select_only(sql)

    # 쿼리 실행 시작
    response = _client.start_query_execution(
        QueryString=sql,
        QueryExecutionContext={"Database": ATHENA_DATABASE},
        WorkGroup=ATHENA_WORKGROUP,
        ResultConfiguration={"OutputLocation": ATHENA_OUTPUT},
    )
    query_execution_id = response["QueryExecutionId"]

    # 쿼리 완료 대기
    _wait_for_query(query_execution_id)

    # 결과 가져오기
    return _fetch_results(query_execution_id)


def _wait_for_query(query_execution_id: str) -> None:
    """Athena 쿼리 완료를 폴링으로 대기한다."""
    elapsed = 0.0
    while elapsed < _MAX_WAIT_SECONDS:
        response = _client.get_query_execution(QueryExecutionId=query_execution_id)
        state = response["QueryExecution"]["Status"]["State"]

        if state == "SUCCEEDED":
            return
        if state in ("FAILED", "CANCELLED"):
            reason = response["QueryExecution"]["Status"].get(
                "StateChangeReason", "알 수 없는 오류"
            )
            raise RuntimeError(f"쿼리 실행 실패: {reason}")

        time.sleep(_POLL_INTERVAL)
        elapsed += _POLL_INTERVAL

    raise RuntimeError(f"쿼리 타임아웃: {_MAX_WAIT_SECONDS}초 초과")


def _fetch_results(query_execution_id: str) -> pd.DataFrame:
    """Athena 쿼리 결과를 DataFrame으로 변환한다."""
    paginator = _client.get_paginator("get_query_results")
    pages = paginator.paginate(QueryExecutionId=query_execution_id)

    rows: list[list[str]] = []
    columns: list[str] = []

    for page in pages:
        result_set = page["ResultSet"]

        # 첫 페이지에서 컬럼명 추출
        if not columns:
            columns = [
                col["Label"]
                for col in result_set["ResultSetMetadata"]["ColumnInfo"]
            ]
            # 첫 번째 행은 헤더이므로 건너뜀
            data_rows = result_set["Rows"][1:]
        else:
            data_rows = result_set["Rows"]

        for row in data_rows:
            rows.append([datum.get("VarCharValue", "") for datum in row["Data"]])

    df = pd.DataFrame(rows, columns=columns)
    # 숫자 컬럼 자동 변환
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col])
        except (ValueError, TypeError):
            pass
    return df
