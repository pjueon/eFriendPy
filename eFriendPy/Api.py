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

from .Core import *
from .Logger import *
import pandas as pd 
from datetime import datetime
import yfinance as yf 
from pandas_datareader import data as pdr 
yf.pdr_override()

class Api():
    """고수준 API
    create_qapplication_internally: Qt5를 사용하기 위해 필요한 QApplication 객체를 내부적으로 생성. 다른 Qt 코드와 연동하기 위해 QApplication 객체를 외부에서 생성한다면 False로 초기화 가능.
    """
    def __init__(self, create_qapplication_internally = True):
        self._core = Core(create_qapplication_internally)
        self.password = "0000"                  # 사용자가 직접 입력해야하는 부분
        self.logger = DefaultLogger()           # 사용자가 logger를 외부에서 수정할 수 있도록함(ex> slack 연동 등)

        def send_log_when_error():
            if self._core.GetRtCode() != "0":
                self.logger("[ERROR] " + self._core.GetReqMessage())

        # 메시지출력 외에 아무일도 안하는 이벤트 핸들러 등록 
        # 이벤트 driven하게 처리하지 않고 그냥 데이터 요청->받기 를 순차적으로 처리하기 위함
        # 아예 핸들러를 등록을 안하면 데이터를 못 받음 (확실하진 않으나 이벤트를 "받았다"는 사실 자체만 중요한 듯함)
        self._core.SetReceiveDataEventHandler(send_log_when_error) 
        self._core.SetReceiveErrorDataEventHandler(send_log_when_error)


    def is_connected(self):
        """eFriend Expert 모듈과 제대로 통신이 되고 있는지 여부를 반환한다
        Account 정보를 가져올 수 있는지 확인하여 통신 여부를 판단.
        """
        accounts = self.get_all_accounts()
        return len(accounts) > 0


    def get_all_accounts(self):
        """모든 계좌번호를 list로 반환한다"""
        account_count = self._core.GetAccountCount()
        return [self._core.GetAccount(i) for i in range(account_count)]


    def set_account_info(self, account):
        """데이터를 요청하기 위해 계좌 정보를 세팅한다"""
        account_num, product_code = self.parse_account_code(account)

        # 파라미터 set
        self._core.SetSingleData(0, account_num)
        self._core.SetSingleData(1, product_code)
        self._core.SetSingleData(2, self._core.GetEncryptPassword(self.password))  


    def parse_account_code(self, account):
        """입력받은 계좌번호를 종합계좌번호와 상품코드로 파싱해서 반환한다"""
        account_num = account[:8]  # 종합계좌번호 (계좌번호 앞 8자리) 
        product_code = account[8:] # 계좌상품코드(종합계좌번호 뒷 부분에 붙는 번호)
        return (account_num, product_code)


    def buy_kr_stock(self, account, product_code, amount, price = 0):
        """국내주식 매수, 설정한 price값이 0 이하이면 시장가로 매수"""
        self.set_account_info(account)
        self._core.SetSingleData(3, product_code)

        order_type = "01" if price <= 0 else "00"    # 주문 구분(메뉴얼 참조), 00: 지정가, 01: 시장가

        self._core.SetSingleData(4, order_type)      
        self._core.SetSingleData(5, str(amount))    # 주문 수량
        self._core.SetSingleData(6, str(price))     # 주문 단가
        self._core.RequestData("SCABO")             # 현금매수 주문

        order_num = self._core.GetSingleData(1, 0)
        return order_num


    def sell_kr_stock(self, account, product_code, amount, price = 0):
        """국내주식 매도, 설정한 price값이 0 이하이면 시장가로 매도"""
        self.set_account_info(account)
        self._core.SetSingleData(3, product_code)

        order_type = "01" if price <= 0 else "00"    # 주문 구분(메뉴얼 참조), 00: 지정가, 01: 시장가

        self._core.SetSingleData(4, "01")           # 매도유형, 01 (고정값으로 추정됨) 
        self._core.SetSingleData(5, order_type)      # 주문 구분(메뉴얼 참조), 00: 지정가, 01: 시장가
        self._core.SetSingleData(6, str(amount))    # 주문 수량
        self._core.SetSingleData(7, str(price))     # 주문 단가
        self._core.RequestData("SCAAO")             # 현금매도 주문

        order_num = self._core.GetSingleData(1, 0)
        return order_num


    def buy_us_stock(self, account, market_code, product_code, amount, price):
        """미국주식 매수, market_code: 해외거래소코드(NASD / NYSE / AMEX 등 4글자 문자열)"""
        self.set_account_info(account)
        self._core.SetSingleData(3, market_code)
        self._core.SetSingleData(4, product_code)
        self._core.SetSingleData(5, str(amount))
        self._core.SetSingleData(6, "{0:.2f}".format(price))    # 소숫점 2자리까지로 설정해야 오류가 안남
        self._core.SetSingleData(9, "0")                        # 주문서버구분코드, 0으로 입력
        self._core.SetSingleData(10, "00")                      # 주문구분, 00: 지정가
        self._core.RequestData("OS_US_BUY")                     # 미국매수 주문

        order_num = self._core.GetSingleData(1, 0)
        return order_num

    def sell_us_stock(self, account, market_code, product_code, amount, price):
        """미국주식 매도, market_code: 해외거래소코드(NASD / NYSE / AMEX 등 4글자 문자열)"""
        self.set_account_info(account)
        self._core.SetSingleData(3, market_code)
        self._core.SetSingleData(4, product_code)
        self._core.SetSingleData(5, str(amount))
        self._core.SetSingleData(6, str(price))
        self._core.SetSingleData(9, "0")           # 주문서버구분코드, 0으로 입력
        self._core.SetSingleData(10, "00")         # 주문구분, 00: 지정가
        self._core.RequestData("OS_US_SEL")        # 미국매도 주문

        order_num = self._core.GetSingleData(1, 0)
        return order_num

    def get_processed_us_orders(self, account, market_code, start_date = None):
        """미국주식 체결 내역 조회, market_code: 해외거래소코드(NASD / NYSE / AMEX 등 4글자 문자열)"""
        today = datetime.today().strftime("%Y%m%d")

        if start_date is None:
            start_date = today   # 오늘
        
        end_date = today         # 오늘
        self.set_account_info(account)

        self._core.SetSingleData(4, start_date)
        self._core.SetSingleData(5, end_date)
        self._core.SetSingleData(6, "00")          # 00: 전체, 01: 매도, 02: 매수
        self._core.SetSingleData(7, "01")          # 00: 전체, 01: 체결, 02: 미체결
        self._core.SetSingleData(8, market_code) 

        self._core.RequestData("OS_US_CCLD")       # 미국 체결 내역 조회

        # 데이터 받아오기
        record_count = self._core.GetMultiRecordCount(0)
        res = pd.DataFrame(index=range(record_count), columns=["주문일자", "주문번호", "원주문번호", "상품번호", "매수매도구분코드명", "주문수량", "체결단가"])
        for record_idx in range(record_count):
            date = self._core.GetMultiData(0, record_idx, 0, 0)
            order_num = self._core.GetMultiData(0, record_idx, 2, 0)
            org_order_num = self._core.GetMultiData(0, record_idx, 3, 0)
            product_num = self._core.GetMultiData(0, record_idx, 12, 0)
            buy_or_sell = self._core.GetMultiData(0, record_idx, 5, 0)
            order_amount = self._core.GetMultiData(0, record_idx, 10, 0)
            price =  self._core.GetMultiData(0, record_idx, 13, 0)

            res.loc[record_idx] = [date, order_num, org_order_num, product_num, buy_or_sell, order_amount, price]

        return res

    def get_processed_kr_orders(self, account, start_date = None):
        """국내 주식 체결 내역 조회"""
        today = datetime.today().strftime("%Y%m%d")
        if start_date is None:
            start_date = today    # 오늘
        
        end_date = today          # 오늘
        self.set_account_info(account)

        self._core.SetSingleData(3, start_date)
        self._core.SetSingleData(4, end_date)

        self._core.SetSingleData(5, "00")  # 매도매수구분코드. 전체: 00, 매도: 01, 매수: 02
        self._core.SetSingleData(6, "00")  # 조회구분.        역순: 00, 정순: 01
        self._core.SetSingleData(8, "01")  # 체결구분.        전체: 00, 체결: 01, 미체결: 02
        self._core.RequestData("TC8001R")  # 주식 일별 주문 체결 조회 (3개월 이내)

        # 데이터 받아오기
        record_count = self._core.GetMultiRecordCount(0)
        res = pd.DataFrame(index=range(record_count), columns=["주문일자", "주문번호", "원주문번호", "상품번호", "매수매도구분코드명", "주문수량"])
        for record_idx in range(record_count):
            date = self._core.GetMultiData(0, record_idx, 0, 0)
            order_num = self._core.GetMultiData(0, record_idx, 2, 0)
            org_order_num = self._core.GetMultiData(0, record_idx, 3, 0)
            product_num = self._core.GetMultiData(0, record_idx, 7, 0)
            buy_or_sell = self._core.GetMultiData(0, record_idx, 6, 0)
            order_amount = self._core.GetMultiData(0, record_idx, 9, 0)

            res.loc[record_idx] = [date, order_num, org_order_num, product_num, buy_or_sell, order_amount]

        return res


    def get_unprocessed_us_orders(self, account, market_code):
        """미국 주식 미체결 내역 조회, marketCode: 해외거래소코드(NASD / NYSE / AMEX 등 4글자 문자열)"""
        self.set_account_info(account)
        self._core.RequestData("OS_US_NCCS") # 미국 미체결 조회

        # 데이터 받아오기
        record_count = self._core.GetMultiRecordCount(0)
        res = pd.DataFrame(index=range(record_count), columns=["주문일자", "주문번호", "원주문번호", "상품번호", "매수매도구분코드명", "주문수량"])
        for record_idx in range(record_count):
            date = self._core.GetMultiData(0, record_idx, 0, 0)
            order_num = self._core.GetMultiData(0, record_idx, 2, 0)
            org_order_num = self._core.GetMultiData(0, record_idx, 3, 0)
            product_num = self._core.GetMultiData(0, record_idx, 5, 0)
            buy_or_sell = self._core.GetMultiData(0, record_idx, 7, 0)
            order_amount = self._core.GetMultiData(0, record_idx, 17, 0)

            res.loc[record_idx] = [date, order_num, org_order_num, product_num, buy_or_sell, order_amount]

        return res

    def get_unprocessed_kr_orders(self, account):
        """국내 주식 미체결 내역 조회
        (정정 취소 가능 주문 조회)
        """
        self.set_account_info(account)
        self._core.SetSingleData(5, "0")  # 조회구분. 주문순: 0, 종목순: 1
        self._core.RequestData("SMCP") # 국내주식 정정 취소 가능 주문 조회

        # 데이터 받아오기
        record_count = self._core.GetMultiRecordCount(0)
        res = pd.DataFrame(index=range(record_count), columns=["주문번호", "원주문번호", "상품번호", "매수매도구분코드명", "주문수량"])
        for record_idx in range(record_count):
            order_num = self._core.GetMultiData(0, record_idx, 1, 0)
            org_order_num = self._core.GetMultiData(0, record_idx, 2, 0)
            product_num = self._core.GetMultiData(0, record_idx, 4, 0)
            buy_or_sell = self._core.GetMultiData(0, record_idx, 13, 0)
            order_amount = self._core.GetMultiData(0, record_idx, 7, 0)

            if order_num == "":
                res = res.iloc[:record_idx]
                break

            res.loc[record_idx] = [order_num, org_order_num, product_num, buy_or_sell, order_amount]

        return res



    def cancel_us_order(self, account, market_code, product_code, org_order_num, amount):
        """미국 주식 주문을 취소한다, market_code: 해외거래소코드(NASD / NYSE / AMEX 등 4글자 문자열)"""
        self.set_account_info(account)
        self._core.SetSingleData(3, market_code)
        self._core.SetSingleData(4, product_code)
        self._core.SetSingleData(5, org_order_num)
        self._core.SetSingleData(6, "02")       # 02 : 취소, 01 : 정정 
        self._core.SetSingleData(7, str(amount))

        self._core.RequestData("OS_US_CNC")



    def cancel_kr_order(self, account, org_order_num, amount):
        """국내 주식 주문을 취소한다."""
        self.set_account_info(account)
        self._core.SetSingleData(4, org_order_num)
        self._core.SetSingleData(5, "00")       # 주문 구분, 취소인 경우는 00
        self._core.SetSingleData(5, "02")       # 정정취소구분코드. 02: 취소, 01: 정정
        self._core.SetSingleData(7, amount)     # 주문수량

        self._core.RequestData("SMCO")          # 국내 주식 주문 정정 취소
        

    def cancel_all_us_orders(self, account, market_code):
        """미체결 미국 주식 주문을 모두 취소한다, market_code: 해외거래소코드(NASD / NYSE / AMEX 등 4글자 문자열)"""
        unprocessed = self.get_unprocessed_us_orders(account, market_code)

        for i in unprocessed.index:
            org_order_num = unprocessed.loc[i, "원주문번호"]
            if org_order_num == "":
                org_order_num = unprocessed.loc[i, "주문번호"]

            product_code = unprocessed.loc[i, "상품번호"]
            amount = unprocessed.loc[i, "주문수량"]

            self.cancel_kr_order(account, market_code, product_code, org_order_num, amount)

    def cancel_all_kr_orders(self, account):
        """미체결 국내 주식 주문을 모두 취소한다."""
        unprocessed = self.get_unprocessed_kr_orders(account)

        for i in unprocessed.index:
            org_order_num = unprocessed.loc[i, "원주문번호"]
            if org_order_num == "":
                org_order_num = unprocessed.loc[i, "주문번호"]

            amount = unprocessed.loc[i, "주문수량"]

            self.cancel_kr_order(account, org_order_num, amount)
        

    def get_kr_stock_price(self, stock_code):
        """종목코드(문자열)에 해당하는 국내주식 현재가 시세 반환"""
        self._core.SetSingleData(0, "J")               # 시장분류코드, J: 주식, ETF, ETN
        self._core.SetSingleData(1, stock_code)
        self._core.RequestData("SCP")                  # 현재가 시세 요청

        return int(self._core.GetSingleData(11, 0))    # 현재가 데이터 반환


    def get_us_stock_price(self, stock_code):
        """종목코드(문자열)에 해당하는 미국주식 현재가 반환 (yahoo finance 사용)"""
        today = datetime.today().strftime("%Y-%m-%d")
        df = pdr.get_data_yahoo(stock_code, start=today)
        if len(df) == 0:
            return Exception("미국 주식 {0} 의 현재가를 가져오는데 실패했습니다.".format(stock_code))

        return df["Close"].iloc[0]


    def get_usd_to_krw_rate(self, account):
        """1 달러 -> 원으로 환전할때의 현재 기준 예상환율을 반환
        예상환율은 최초고시 환율로 매일 08:15시경에 당일 환율이 제공됨
        """
        self.set_account_info(account)
        self._core.SetSingleData(3, "512")          # 미국: 512, 홍콩: 501, 중국: 551, 일본: 515
        self._core.RequestData("OS_OS3004R")        # 해외증거금조회

        rate = self._core.GetMultiData(3, 0, 4, 0)  # 예상환율

        return float(rate)

    def get_kr_total_evaluated_price(self, account):
        """해당 계좌의 국내 주식(+원화예수금) 총평가금액을 반환"""
        deposit = self.get_kr_buyable_cash(account)
        stocks = self.get_kr_stock_balance(account)

        return deposit + stocks["평가금액"].sum()


    def get_us_total_evaluated_price(self, account):
        """해당 계좌의 미국 주식(+주문가능 달러예수금) 총평가금액을 반환"""
        deposit = self.get_us_buyable_cash(account)
        stocks = self.get_us_stock_balance(account)

        return deposit + stocks["평가금액"].sum()

    def get_kr_buyable_cash(self, account):
        """주문가능 현금 반환(원화)"""
        self.set_account_info(account)
        self._core.SetSingleData(5, "01")
        self._core.RequestData("SCAP")

        return int(self._core.GetSingleData(0, 0))  # 주문가능현금

    def get_us_buyable_cash(self, account):
        """주문 가능한 현금 반환(USD)"""  
        # 데이터 요청
        self.set_account_info(account)   
        self._core.RequestData("OS_US_DNCL")

        # 데이터 받아오기
        record_count = self._core.GetMultiRecordCount(0)

        for record_idx in range(record_count):
            currency_code = self._core.GetMultiData(0, record_idx, 0, 0)
            if currency_code != "USD":
                continue
            
            cash = self._core.GetMultiData(0, record_idx, 4, 0)  # 외화주문가능금액
            return float(cash)

        return 0.0


    def get_kr_stock_balance(self, account):
        """국내주식 잔고 정보를 반환하는 함수
        각 보유 종목들에 대한 내용을 DataFrame 형태로 반환한다
        """
        # 데이터 요청
        self.set_account_info(account)   
        self._core.RequestData("SATPS")           # 국내주식 잔고 현황

        # 데이터 받아오기
        # 보유 주식 정보
        record_count = self._core.GetMultiRecordCount(0)
        stocks = pd.DataFrame(index=range(record_count), columns=["종목코드", "종목명", "현재가", "보유수량", "평가금액"])

        for record_idx in range(record_count):
            product_num = self._core.GetMultiData(0, record_idx, 0, 0)
            product_name = self._core.GetMultiData(0, record_idx, 1, 0)
            current_price = self._core.GetMultiData(0, record_idx, 11, 0)
            hold = self._core.GetMultiData(0, record_idx, 7, 0)
            eval_price = self._core.GetMultiData(0, record_idx, 12, 0)

            # 실패했을때에 대한 예외처리
            if product_num == "":        
                stocks = stocks.iloc[:record_idx]
                break

            stocks.loc[record_idx] = [product_num, product_name, int(current_price), int(hold), int(eval_price)]

        return stocks


    def get_us_stock_balance(self, account):
        """미국주식 잔고 정보를 반환하는 함수
        각 보유 종목들에 대한 내용을 DataFrame 형태로 반환한다
        """
        # 데이터 요청
        self.set_account_info(account)  
        self._core.RequestData("OS_US_CBLC")           # 미국주식 잔고 현황

        # 데이터 받아오기 
        # 보유 주식 정보
        record_count = self._core.GetMultiRecordCount(0)
        stocks = pd.DataFrame(index=range(record_count), columns=["해외거래소코드","종목코드", "종목명", "현재가", "보유수량", "평가금액"])

        for record_idx in range(record_count):
            market_code = self._core.GetMultiData(0, record_idx, 14, 0)
            product_num = self._core.GetMultiData(0, record_idx, 3, 0)
            product_name = self._core.GetMultiData(0, record_idx, 4, 0)
            current_price = self._core.GetMultiData(0, record_idx, 12, 0)
            hold = self._core.GetMultiData(0, record_idx, 8, 0)
            eval_price = self._core.GetMultiData(0, record_idx, 11, 0)

            # recordCount가 실제 보유 종목수와 상관없이 100으로 들어가는듯함. 이에 대한 예외처리
            if product_num == "":        
                stocks = stocks.iloc[:record_idx]
                break

            stocks.loc[record_idx] = [market_code, product_num, product_name, float(current_price), int(hold), float(eval_price)]

        return stocks


   
        