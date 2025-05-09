import yfinance as yf
import pandas_ta as ta
import pandas as pd
from datetime import datetime, timedelta
import pymysql

# conn = pymysql.connect(host='127.0.0.1', user='root', password='jun12160', db='stock', charset='utf8')
# cursor = conn.cursor()
#
# conn = pymysql.connect(host='127.0.0.1', user='root', password='jun12160', db='stock', charset='utf8')
# cursor = conn.cursor()
#
# table_name = "jun_stock_list"
# # stock_list 테이블에서 종목 코드 읽어오기
# cursor.execute(f"SELECT code FROM {table_name}")
# stock_codes = cursor.fetchall()  # 튜플 리스트 반환
# stock_codes = [code[0] for code in stock_codes]
#
# cursor.execute(f"SELECT name FROM {table_name}")
# stock_names = cursor.fetchall()  # 튜플 리스트 반환
# stock_names = [name[0] for name in stock_names]
#
# for i in range(0,len(stock_codes)):
#     code = stock_codes[i]
#     name = stock_names[i]
#
#     ticker = yf.Ticker(code)
#     # 주봉 데이터
#     df = ticker.history(period="1y")
#     print(df['Close'].iloc[-1])

# # 주식 코드 리스트
# stock_codes = ["005930.KS"]
#
# # 각 주식 코드에 대해 데이터 가져오기 및 RSI 계산
# for code in stock_codes:
#     ticker = yf.Ticker(code)
#     df = ticker.history(period="2y",interval="1wk")
#     df['RSI'] = ta.rsi(df['Close'], length=14)
#     bbands = ta.bbands(df['Close'], length=40, stddev=2)
#     df['BB_Lower'] = bbands['BBL_40_2.0']  # 하단 밴드
#     latest_bb_lower = df['BB_Lower'].iloc[-1]
#     print(latest_bb_lower)
#
#     df['SMA'] = ta.sma(df['Close'], length=20)
#     SMA = df['SMA'].iloc[-1]


# MySQL 연결
conn = pymysql.connect(host='127.0.0.1', user='root', password='jun12160', db='stock', charset='utf8')
cursor = conn.cursor()

table_name = f"jun_stock_list"
# stock_list 테이블에서 종목 코드 읽어오기
cursor.execute(f"SELECT code FROM {table_name}")
stock_codes = cursor.fetchall()  # 튜플 리스트 반환
stock_codes = [code[0] for code in stock_codes]

cursor.execute(f"SELECT name FROM {table_name}")
stock_names = cursor.fetchall()  # 튜플 리스트 반환
stock_names = [name[0] for name in stock_names]

for i in range(0,len(stock_codes)):
    code = stock_codes[i]
    name = stock_names[i]

    ticker = yf.Ticker(code)
    # 일봉 데이터
    df2 = ticker.history(period="2y", interval="1wk")

    price = df2['Close'].iloc[-1]
    bbands = ta.bbands(df2['Close'], length=40, stddev=2)
    df2['BB_Lower'] = bbands['BBL_40_2.0']  # 하단 밴드
    bol = df2['BB_Lower'].iloc[-1]

    print(name,bol)


# 연결 종료
cursor.close()
conn.close()


