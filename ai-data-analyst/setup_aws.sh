#!/bin/bash
# AWS 인프라 셋업 스크립트 — AI 데이터 분석가 챗봇
# 사용법: source setup_aws.sh
#
# 사전 조건: AWS credentials가 환경변수로 설정되어 있어야 함
#   export AWS_DEFAULT_REGION="us-east-1"
#   export AWS_ACCESS_KEY_ID="..."
#   export AWS_SECRET_ACCESS_KEY="..."
#   export AWS_SESSION_TOKEN="..."

set -e

REGION="${AWS_DEFAULT_REGION:-us-east-1}"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
DATA_BUCKET="aidlc-workshop-data-${ACCOUNT_ID}"
RESULTS_BUCKET="aidlc-workshop-athena-results-${ACCOUNT_ID}"
DATABASE="aidlc_workshop"
TABLE="fact_events"

echo "=== AI 데이터 분석가 챗봇 — AWS 셋업 ==="
echo "Region: ${REGION}"
echo "Account: ${ACCOUNT_ID}"
echo "Data Bucket: ${DATA_BUCKET}"
echo ""

# 1. S3 버킷 생성
echo "[1/5] S3 버킷 생성..."
aws s3 mb "s3://${DATA_BUCKET}" --region "${REGION}" 2>/dev/null || echo "  → 이미 존재함"
aws s3 mb "s3://${RESULTS_BUCKET}" --region "${REGION}" 2>/dev/null || echo "  → 이미 존재함"

# 2. CSV 데이터 업로드
echo "[2/5] fact_events.csv 업로드..."
aws s3 cp data/fact_events.csv "s3://${DATA_BUCKET}/fact_events/fact_events.csv"

# 3. Glue Database 생성
echo "[3/5] Glue Database 생성..."
aws athena start-query-execution \
  --query-string "CREATE DATABASE IF NOT EXISTS ${DATABASE}" \
  --result-configuration "OutputLocation=s3://${RESULTS_BUCKET}/setup/" \
  --region "${REGION}" \
  --output text
sleep 3

# 4. Glue Table 생성 (Athena DDL)
echo "[4/5] Glue Table 생성..."
DDL="CREATE EXTERNAL TABLE IF NOT EXISTS ${DATABASE}.${TABLE} (
  customer_id BIGINT,
  age INT,
  gender STRING,
  loyalty_member STRING,
  product_type STRING,
  sku STRING,
  rating INT,
  order_status STRING,
  payment_method STRING,
  total_price DOUBLE,
  unit_price DOUBLE,
  quantity INT,
  purchase_date DATE,
  shipping_type STRING,
  add_ons_purchased STRING,
  add_on_total DOUBLE
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES ('separatorChar' = ',', 'quoteChar' = '\"', 'escapeChar' = '\\\\')
STORED AS TEXTFILE
LOCATION 's3://${DATA_BUCKET}/fact_events/'
TBLPROPERTIES ('skip.header.line.count'='1');"

aws athena start-query-execution \
  --query-string "${DDL}" \
  --query-execution-context "Database=${DATABASE}" \
  --result-configuration "OutputLocation=s3://${RESULTS_BUCKET}/setup/" \
  --region "${REGION}" \
  --output text
sleep 5

# 5. 테스트 쿼리
echo "[5/5] 테스트 쿼리 실행..."
QUERY_ID=$(aws athena start-query-execution \
  --query-string "SELECT COUNT(*) AS total_rows FROM ${DATABASE}.${TABLE}" \
  --query-execution-context "Database=${DATABASE}" \
  --result-configuration "OutputLocation=s3://${RESULTS_BUCKET}/setup/" \
  --region "${REGION}" \
  --query "QueryExecutionId" \
  --output text)

echo "  Query ID: ${QUERY_ID}"
sleep 5

STATUS=$(aws athena get-query-execution --query-execution-id "${QUERY_ID}" --query "QueryExecution.Status.State" --output text)
echo "  Status: ${STATUS}"

if [ "${STATUS}" = "SUCCEEDED" ]; then
  RESULT=$(aws athena get-query-results --query-execution-id "${QUERY_ID}" --query "ResultSet.Rows[1].Data[0].VarCharValue" --output text)
  echo "  ✅ 총 행 수: ${RESULT}"
else
  echo "  ⚠️ 쿼리 상태: ${STATUS} — 잠시 후 Athena 콘솔에서 확인하세요"
fi

echo ""
echo "=== 셋업 완료 ==="
echo ""
echo "config.yaml 업데이트 필요:"
echo "  athena.output_location: s3://${RESULTS_BUCKET}/query-results/"
echo "  s3.data_bucket: ${DATA_BUCKET}"
echo ""
echo "앱 실행:"
echo "  streamlit run src/app.py"
