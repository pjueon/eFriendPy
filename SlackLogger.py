from slack import Slack
from datetime import datetime

class SlackLogger:
    def __init__(self):
        self.slack = Slack()

    def InitSlack(self, token, channel):
        """slack 관련 정보를 초기화한다."""
        self.slack.token = token
        self.slack.channel = channel

    def __call__(self, msg):
        """콘솔과 slack에 로그 메시지를 쓴다"""
        msg = "{0} {1}".format(
            datetime.now().strftime('[%Y/%m/%d %H:%M:%S]'), msg)
        print(msg)
        self.slack.post(msg)

