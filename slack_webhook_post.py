import json
import requests
import configparser


config = configparser.ConfigParser()
config.read('config.ini')

def post_to_slack(self, slack_data):

    # Set the webhook_url to the one provided by Slack when you create the webhook at https://my.slack.com/services/new/incoming-webhook/
    webhook_url =
    slack_data = {'text': ""}

    response = requests.post(
        webhook_url, json=slack_data,
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )