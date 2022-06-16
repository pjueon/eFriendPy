# MIT License
#
# Copyright (c) 2021 Jueon Park
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
        msg = self.format(msg)
        print(msg)
        self.Post(msg)

    def Post(self, msg):
        """slack으로 메시지를 보낸다"""
        response = requests.post("https://slack.com/api/chat.postMessage",
                                 headers={
                                     "Authorization": "Bearer "+self.token},
                                 data={"channel": self.channel, "text": msg}
                                 )
