import os

import boto3


def send_notification(recipient, subject, body):
    sender = os.getenv("SES_SENDER_EMAIL")
    region = os.getenv("AWS_REGION", "ap-south-1")

    if not sender:
        raise RuntimeError("SES_SENDER_EMAIL is not configured")

    ses = boto3.client("ses", region_name=region)
    return ses.send_email(
        Source=sender,
        Destination={"ToAddresses": [recipient]},
        Message={
            "Subject": {"Data": subject, "Charset": "UTF-8"},
            "Body": {"Text": {"Data": body, "Charset": "UTF-8"}},
        },
    )
