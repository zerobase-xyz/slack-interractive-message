from flask import Flask, request, make_response, Response
import os
import json
import boto3

# Your app's Slack bot user token
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]
SLACK_CHANNEL_ID = ""
AUTH_FAILED = "Authentication failed"
INVAILD_REQUEST = "invaild reques"
RESPONSE_TEXT = "Are you sure you want to update ecs service ?"

# Slack client for Web API requests
slack_client = SlackClient(SLACK_BOT_TOKEN)

# The endpoint Slack will load your menu options from
attachments_json = [
        {
            "text": "operator:{} servicename:{} desired:{}".format(
                user_name,
                service_name,
                count),
            "fallback": "You are unable to choose",
            "callback_id": "ecs_update_call_back",
            "color": "#3AA3E3",
            "attachment_type": "default",
            "actions": [
                {
                    "name": "approve",
                    "text": "Approve",
                    "style": "primary",
                    "type": "button",
                    "value": "approve"
                },
                {
                    "name": "reject",
                    "text": "Reject",
                    "style": "danger",
                    "type": "button",
                    "value": "reject"
                }
            ]
        }
    ]


# Helper for verifying that requests came from Slack
def verify_slack_token(req_token, req_channel_id):
    if SLACK_VERIFICATION_TOKEN != req_token \
            or SLACK_CHANNEL_ID != req_channel_id:
        return make_response("Request {}".format(AUTH_FAILED), 403)

def lambda_handler(event, context):
    return handler(event["querystring"])

def handler(event):
    verify_slack_token(
            event["token"],
            event["channel_id"]
            )

    # Parse the request parameter
    user_name = event["user_name"]
    text = event["text"]

    split_text = text.split("+")
    service_name, count = split_text[0], split_text[1]

    slack_client.api_call(
            "chat.postMessage",
            channel=SLACK_CHANNEL_ID,
            text=RESPOSE_TEXT
            attachments=attachments_json
            )
    # Load options dict as JSON and respond to Slack
    return 
