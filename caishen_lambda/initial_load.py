from caishen_dashboard.data_processing.stock import StockHistoryRequestBuilder
from caishen_dashboard.data_processing.constants import DateRange, StockInterval
import requests
import json
import boto3
import os
import logging
from botocore.exceptions import ClientError
import io
import codecs


S3_CLIENT = boto3.client("s3")
BUCKET = os.environ["BUCKET"]


def stock_retrival(event, context):
    tickers = [event["tickers"]]
    details = StockHistoryRequestBuilder(tickers=tickers,
                                         date_range=DateRange.fiveYear,
                                         interval=StockInterval.oneDay)
    conf = details.conf
    rapid_api_response = requests.request("GET", conf["url"], headers=conf["headers"],
                                          params=conf["querystring"])
    contents = json.loads(rapid_api_response.text)

    for ticker in contents.keys():
        temp_details = contents[ticker]
        buffer = io.BytesIO()
        writer = codecs.getwriter("utf-8")
        wrapper = writer(buffer)

        wrapper.write(",".join(["timestamp", "close\n"]))
        for i in range(len(temp_details["timestamp"])):
            wrapper.write(",".join([str(temp_details["timestamp"][i]), str(temp_details["close"][i]) + "\n"]))

        try:
            S3_CLIENT.put_object(Body=wrapper.getvalue(),
                                 Bucket=BUCKET,
                                 Key=f"{ticker}/data.csv")

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
