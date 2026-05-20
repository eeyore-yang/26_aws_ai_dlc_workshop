"""AWS 인프라 셋업 스크립트 — S3 + Glue + Athena."""
import os
import time

import boto3

REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
ACCOUNT_ID = boto3.client("sts", region_name=REGION).get_caller_identity()["Account"]

DATA_BUCKET = f"aidlc-workshop-data-{ACCOUNT_ID}"
RESULTS_BUCKET = f"aidlc-workshop-athena-results-{ACCOUNT_ID}"
DATABASE = "aidlc_workshop"
TABLE = "fact_events"

s3 = boto3.client("s3", region_name=REGION)
athena = boto3.client("athena", region_name=REGION)


def create_bucket(bucket_name: str) -> None:
    try:
        if REGION == "us-east-1":
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": REGION},
            )
        print(f"  ✅ Created: {bucket_name}")
    except s3.exceptions.BucketAlreadyOwnedByYou:
        print(f"  → Already exists: {bucket_name}")
    except Exception as e:
        print(f"  ⚠️ {e}")


def upload_csv() -> None:
    csv_path = os.path.join(os.path.dirname(__file__), "data", "fact_events.csv")
    s3.upload_file(csv_path, DATA_BUCKET, "fact_events/fact_events.csv")
    print(f"  ✅ Uploaded: fact_events.csv → s3://{DATA_BUCKET}/fact_events/")


def run_athena_query(sql: str, wait: bool = True) -> str:
    resp = athena.start_query_execution(
        QueryString=sql,
        ResultConfiguration={"OutputLocation": f"s3://{RESULTS_BUCKET}/setup/"},
    )
    qid = resp["QueryExecutionId"]
    if wait:
        while True:
            status = athena.get_query_execution(QueryExecutionId=qid)
            state = status["QueryExecution"]["Status"]["State"]
            if state in ("SUCCEEDED", "FAILED", "CANCELLED"):
                break
            time.sleep(1)
        if state != "SUCCEEDED":
            reason = status["QueryExecution"]["Status"].get("StateChangeReason", "")
            print(f"  ⚠️ Query {state}: {reason}")
        return state
    return "RUNNING"


def main() -> None:
    print(f"=== AI 데이터 분석가 — AWS 인프라 셋업 ===")
    print(f"Region: {REGION} | Account: {ACCOUNT_ID}")
    print()

    print("[1/5] S3 버킷 생성...")
    create_bucket(DATA_BUCKET)
    create_bucket(RESULTS_BUCKET)

    print("[2/5] CSV 데이터 업로드...")
    upload_csv()

    print("[3/5] Glue Database 생성...")
    state = run_athena_query(f"CREATE DATABASE IF NOT EXISTS {DATABASE}")
    print(f"  ✅ Database: {state}")

    print("[4/5] Glue Table 생성...")
    ddl = f"""
    CREATE EXTERNAL TABLE IF NOT EXISTS {DATABASE}.{TABLE} (
      `Customer ID` BIGINT,
      `Age` INT,
      `Gender` STRING,
      `Loyalty Member` STRING,
      `Product Type` STRING,
      `SKU` STRING,
      `Rating` INT,
      `Order Status` STRING,
      `Payment Method` STRING,
      `Total Price` DOUBLE,
      `Unit Price` DOUBLE,
      `Quantity` INT,
      `Purchase Date` STRING,
      `Shipping Type` STRING,
      `Add-ons Purchased` STRING,
      `Add-on Total` DOUBLE
    )
    ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
    WITH SERDEPROPERTIES (
      'separatorChar' = ',',
      'quoteChar' = '"'
    )
    STORED AS TEXTFILE
    LOCATION 's3://{DATA_BUCKET}/fact_events/'
    TBLPROPERTIES ('skip.header.line.count'='1')
    """
    state = run_athena_query(ddl)
    print(f"  ✅ Table: {state}")

    print("[5/5] 테스트 쿼리...")
    state = run_athena_query(f"SELECT COUNT(*) AS total FROM {DATABASE}.{TABLE}")
    if state == "SUCCEEDED":
        # 결과 가져오기
        resp = athena.start_query_execution(
            QueryString=f"SELECT COUNT(*) AS total FROM {DATABASE}.{TABLE}",
            ResultConfiguration={"OutputLocation": f"s3://{RESULTS_BUCKET}/setup/"},
        )
        qid = resp["QueryExecutionId"]
        while True:
            s = athena.get_query_execution(QueryExecutionId=qid)["QueryExecution"]["Status"]["State"]
            if s in ("SUCCEEDED", "FAILED", "CANCELLED"):
                break
            time.sleep(1)
        if s == "SUCCEEDED":
            results = athena.get_query_results(QueryExecutionId=qid)
            count = results["ResultSet"]["Rows"][1]["Data"][0]["VarCharValue"]
            print(f"  ✅ 총 행 수: {count}")
    else:
        print(f"  ⚠️ 테스트 쿼리 상태: {state}")

    print()
    print("=== 셋업 완료 ===")
    print(f"Data Bucket: s3://{DATA_BUCKET}/fact_events/")
    print(f"Results Bucket: s3://{RESULTS_BUCKET}/query-results/")
    print(f"Database: {DATABASE}")
    print(f"Table: {DATABASE}.{TABLE}")


if __name__ == "__main__":
    main()
