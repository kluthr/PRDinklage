import os
import json
import logging
from pr_dinklage import PRDinklage


def dinklage_handler(event, context):
    try:
        slack_event = json.loads(event['body'])
        if 'challenge' in slack_event:
            return {'body': slack_event['challenge']}
        
        text = slack_event['event']['text']
        print(text)
        
        if 'bot_id' in slack_event['event'] or 'bot_id' in slack_event:
            print('bot id!')
            return '200 OK'

        channel_id = slack_event['event']['channel']

        dinklage = PRDinklage(channel_id, text)
        dinklage.parse_command()

        return '200 OK'
    except Exception as e:
        print(e)
