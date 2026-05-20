"""Athena 테이블 재생성 — 언더스코어 컬럼명."""
import time
import boto3

REGION = "us-east-1"
OUTPUT = "s3://aidlc-workshop-athena-results-251165958261/setup/"
DATA_BUCKET = "aidlc-workshop-data-251165958261"

athena = boto3.client("athena", region_name=REGION)


def run(sql):
    r = athena.start_query_execution(
        QueryString=sql,
        ResultConfiguration={"OutputLocation": OUTPUT},
    )
    qid = r["QueryExecutionId"]
    while True:
        s = athena.get_query_execution(QueryExecutionId=qid)["QueryExecution"]["Status"]["State"]
        if s in ("SUCCEEDED", "FAILED", "CANCELLED"):
            break
        time.sleep(1)
    if s != "SUCCEEDED":
        info = athena.get_query_execution(QueryExecutionId=qid)["QueryExecution"]["Status"]
        print(f"  FAILED: {info.get('StateChangeReason', '')}")
    return s


print("[1] Dropping old table...")
print(f"  {run('DROP TABLE IF EXISTS aidlc_workshop.fact_events')}")

print("[2] Creating table with underscore columns...")
ddl = f"""
CREATE EXTERNAL TABLE aidlc_workshop.fact_events (
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
  purchase_date STRING,
  shipping_type STRING,
  add_ons_purchased STRING,
  add_on_total DOUBLE
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES ('separatorChar' = ',', 'quoteChar' = '"')
STORED AS TEXTFILE
LOCATION 's3://{DATA_BUCKET}/fact_events/'
TBLPROPERTIES ('skip.header.line.count'='1')
"""
print(f"  {run(ddl)}")

print("[3] Test query...")
test_sql = "SELECT product_type, SUM(CAST(total_price AS DOUBLE)) AS revenue FROM aidlc_workshop.fact_events WHERE order_status='Completed' GROUP BY product_type ORDER BY revenue DESC"
state = run(test_sql)
print(f"  {state}")

if state == "SUCCEEDED":
    # Get results
    r = athena.start_query_execution(QueryString=test_sql, ResultConfiguration={"OutputLocation": OUTPUT})
    qid = r["QueryExecutionId"]
    while True:
        s = athena.get_query_execution(QueryExecutionId=qid)["QueryExecution"]["Status"]["State"]
        if s in ("SUCCEEDED", "FAILED", "CANCELLED"):
            break
        time.sleep(1)
    res = athena.get_query_results(QueryExecutionId=qid)
    print("  Results:")
    for row in res["ResultSet"]["Rows"][:6]:
        vals = [d.get("VarCharValue", "") for d in row["Data"]]
        print(f"    {vals}")

print("\nDone!")
