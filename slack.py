import requests

class Slack:
    def __init__(self):
        self.token = "put_your_token_here"
        self.channel = "put_your_channel_here"

    def post(self, msg):
        """slack으로 메시지를 보낸다"""
        response = requests.post("https://slack.com/api/chat.postMessage",
            headers={"Authorization": "Bearer "+self.token},
            data={"channel": self.channel,"text": msg}
        )