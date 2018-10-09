from flask import Flask, request, make_response, Response
import os
import json
import boto3

from slackclient import SlackClient

# Your app's Slack bot user token
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]
SLACK_CHANNEL_ID = ""
DYNAMODB_TABLENAME = ""
AUTH_FAILED = "Authentication failed"
INVAILD_REQUEST = "invaild reques"

# Slack client for Web API requests
slack_client = SlackClient(SLACK_BOT_TOKEN)

# Flask webserver for incoming traffic from Slack
app = Flask(__name__)


# Helper for verifying that requests came from Slack
def verify_slack_token(req_token, req_channel_id):
    if SLACK_VERIFICATION_TOKEN != req_token \
            or SLACK_CHANNEL_ID != req_channel_id:
        print("Error: invalid verification token!")
        return make_response("Request {}".format(AUTH_FAILED), 403)


# The endpoint Slack will load your menu options from
@app.route("/ecs/update_request", methods=["POST"])
def update_request():
    verify_slack_token(
            request.form["token"],
            request.form["channel_id"]
            )

    # Parse the request parameter
    user_name = request.form["user_name"]
    text = request.form["text"]

    split_text = text.split()
    service_name, count = split_text[0], split_text[1]

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

    slack_client.api_call(
            "chat.postMessage",
            channel=SLACK_CHANNEL_ID,
            text="Are you sure you want to update ecs service ?",
            attachments=attachments_json
            )
    # Load options dict as JSON and respond to Slack
    return make_response("Request Success", 200)


@app.route("/ecs/request_perm", methods=["POST"])
def request_perm():
    # Parse the request payload
    form_json = json.loads(request.form["payload"])

    # Verify that the request came from Slack
    verify_slack_token(
            form_json["token"],
            form_json["channel"]["id"]
            )

    if form_json["actions"][0]["value"] == "approve":
        x_text = "approve"
        p_text = form_json["original_message"]["attachments"][0]["text"]
        param = p_text.split()
        servicename = param[1].split(":")
        desired_count = param[2].split(":")
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(DYNAMODB_TABLENAME)
        service_item = table.get_item(
                Key={"ServiceName": servicename[1]}
                )
        service_param = service_item["Item"]["info"]
        service_param["desired_count"] = desired_count[1]
        clientLambda = boto3.client("lambda")
        clientLambda.invoke(
            FunctionName="ecs-update",
            InvocationType="Event",
            Payload=json.dumps(service_param)
        )
    else:
        x_text = "reject"

    # Send an HTTP 200 response with empty body so Slack knows we're done here
    return make_response(x_text, 200)


# Start the Flask server
if __name__ == "__main__":
    app.run()
