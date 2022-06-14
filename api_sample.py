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
    # api.logger = SlackLogger("put_your_token_here", "put_your_channel_here")

    # ===== API 사용 예시 ======
    print(f"eFriend expert 연결 여부: {api.IsConnected()}")
    Accounts = api.GetAllAccounts()
    print(f"보유 계좌들: {Accounts}")

    # 계좌 비밀번호 4자리 세팅
    api.Password = "0000"

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
