import requests
from eFriendPy.Logger import DefaultLogger

# 사용자 정의 Logger의 예시

class SlackLogger(DefaultLogger):
    def __init__(self, token, channel):
        """slack token, channel 초기화"""
        self.token = token
        self.channel = channel

    def __call__(self, msg):
        """콘솔과 slack에 로그 메시지를 쓴다"""
        msg = self.Format(msg)
        print(msg)
        self.Post(msg)

    def Post(self, msg):
        """slack으로 메시지를 보낸다"""
        response = requests.post("https://slack.com/api/chat.postMessage",
                                 headers={
                                     "Authorization": "Bearer "+self.token},
                                 data={"channel": self.channel, "text": msg}
                                 )
