from caishen_dashboard.data_processing.stock import StockHistoryRequestBuilder
from caishen_dashboard.data_processing.constants import DateRange, StockInterval
import requests
import json
import boto3
import io
from datetime import datetime
import os
from botocore.exceptions import ClientError
import logging


S3_CLIENT = boto3.client("s3")
BUCKET = os.environ["BUCKET"]


def retrieve_latest_date(ticker, file_name):
    data_io = io.BytesIO()
    S3_CLIENT.download_fileobj(BUCKET, f"raw/{ticker}/{file_name}", data_io)
    content = json.loads(data_io.getvalue())
    latest = content["timestamp"][-1]
    return datetime.fromtimestamp(latest)


def stock_retrival(event, context):
    tickers = [event["tickers"]]
    current_time = datetime.now().strftime("%d_%m_%y-%H:%M:%S")

    for ticker in tickers:
        latest = retrieve_latest_date(ticker, event["file_name"])
        details = StockHistoryRequestBuilder(tickers=tickers,
                                             date_range=DateRange.fiveDay,
                                             interval=StockInterval.oneDay)
        conf = details.conf
        rapid_api_response = requests.request("GET", conf["url"], headers=conf["headers"],
                                              params=conf["querystring"])
        contents = json.loads(rapid_api_response.text)
        temp_details = contents[ticker]
        temp_output = json.dumps(temp_details, indent=2).encode("utf-8")
        try:
            S3_CLIENT.put_object(Body=temp_output,
                                 Bucket=BUCKET,
                                 Key=f"raw/{ticker}/{current_time}")
        except ClientError as e:
            logging.error(e)

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "storage": "Success"
        })
    }
