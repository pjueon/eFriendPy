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

import sys
from PyQt5.QtWidgets import QApplication
import eFriendPy

# 로그를 slack으로 받고 싶은 경우 필요함
from SlackLogger import SlackLogger

def main():
    # api 객체 생성
    api = eFriendPy.Api()

    # # 로그를 slack으로 받고 싶은 경우 (예시)
    # api.logger = SlackLogger("put_your_token_here", "put_your_channel_here")

    # ===== API 사용 예시 ======
    print(f"version: {eFriendPy.__version__}")

    isConnected = api.IsConnected()
    print(f"eFriend expert 연결 여부: {isConnected}")
    Accounts = api.GetAllAccounts()
    print(f"보유 계좌들: {Accounts}")

    # 계좌 비밀번호 4자리 세팅
    api.Password = "0000"

    if isConnected == False:
        return

    # 사용할 계좌 
    account = Accounts[0]

    cash_kr = api.GetCashKR(account)
    print(f"주문 가능한 원화: {cash_kr} 원")

    cash_us = api.GetCashUS(account)
    print(f"주문 가능한 달러: {cash_us} 달러")

    rate = api.GetUSDtoKRWRate(account)
    print(f"현재 예상 환율: 1 달러 당 {rate} 원")

    stocks_kr = api.GetKRStocks(account)
    print(f"보유 국내주식: {stocks_kr}")

    stocks_us = api.GetUSStocks(account)
    print(f"보유 미국주식: {stocks_us}")
    



if __name__ == "__main__":
    main()
