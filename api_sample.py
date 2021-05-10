import sys
from PyQt5.QtWidgets import QApplication
from eFriendPy.API import *

# 로그를 slack으로 받고 싶은 경우 필요함
from SlackLogger import SlackLogger

def main():
    # Qt 사용하기 위해서 반드시 필요함
    app = QApplication(sys.argv)    

    # api 객체 생성
    api = HighLevelAPI()

    # # 로그를 slack으로 받고 싶은 경우 (예시)
    # api.logger = SlackLogger()
    # api.logger.InitSlack("put_your_token_here", "put_your_channel_here")

    # ===== API 사용 예시 ======
    print("eFriend expert 연결 여부: {0}".format(api.IsConnected()))
    Accounts = api.GetAllAccounts()
    print("보유 계좌들: {0}".format(Accounts))

    # 계좌 비밀번호 4자리 세팅
    api.Password = "0000"

    # 사용할 계좌 
    account = Accounts[0]

    cash_kr = api.GetCashKR(account)
    print("주문 가능한 원화: {0} 원".format(cash_kr))

    cash_us = api.GetCashUS(account)
    print("주문 가능한 달러: {0} 달러".format(cash_us))

    rate = api.GetUSDtoKRWRate(account)
    print("현재 예상 환율: 1 달러 당 {0} 원".format(rate))

    stocks_kr = api.GetKRStocks(account)
    print("보유 국내주식: {0}".format(stocks_kr))

    stocks_us = api.GetUSStocks(account)
    print("보유 미국주식: {0}".format(stocks_us))
    



if __name__ == "__main__":
    main()
