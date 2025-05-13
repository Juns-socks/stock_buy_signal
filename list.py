import pymysql
import time
from datetime import datetime, timedelta
import requests
import pandas_ta as ta
import yfinance as yf
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

def create_table(person_name):
    # MySQL 연결
    conn = pymysql.connect(host='127.0.0.1', user='root', password='jun12160', db='stock', charset='utf8')
    cursor = conn.cursor()

    table_name = "users"
    cursor.execute(f"SELECT name FROM {table_name}")
    users = cursor.fetchall()  # 튜플 리스트 반환
    users = [name[0] for name in users]
    if person_name not in users:
        return

    table_name = f"{person_name}_stock_list"

    create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            code VARCHAR(10) NOT NULL,
            name VARCHAR(255) NOT NULL
        );
        """
    # 테이블 생성 실행
    cursor.execute(create_table_sql)
    conn.commit()

    # 연결 종료
    cursor.close()
    conn.close()

def reset_table(name):
    # MySQL 연결
    conn = pymysql.connect(host='127.0.0.1', user='root', password='jun12160', db='stock', charset='utf8')
    cursor = conn.cursor()

    table_name = f"{name}_stock_list"

    # 기존 테이블 삭제
    drop_table_sql = f"DROP TABLE IF EXISTS {table_name}"
    cursor.execute(drop_table_sql)
    conn.commit()

    # 연결 종료
    cursor.close()
    conn.close()

def make_list(cnt,person_name,num1,num2,kiwoom):
    #시가총액 일정 이상 or 상장일 일정 이하
    print(cnt,person_name,num1,num2)
    # MySQL 연결
    conn = pymysql.connect(host='127.0.0.1', user='root', password='jun12160', db='stock', charset='utf8')
    cursor = conn.cursor()

    table_name = f"{person_name}_stock_list"

    #존재성 확인
    cursor.execute("SHOW TABLES LIKE %s", (table_name,))
    result = cursor.fetchone()

    if not result:
        print(f"Table {table_name} 존재하지 않음")
        return

    #안에 차있는지 확인
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]

    if(count > 0 ):
        print(f"Table {table_name} 에 이미 원소가 들어있습니다")
        return

    # 주식 코드 리스트 가져오기
    kospi_code_list = kiwoom.GetCodeListByMarket('0')
    kosdaq_code_list = kiwoom.GetCodeListByMarket('10')
    code_list = kospi_code_list + kosdaq_code_list
    check_name = ["스팩", "레버리지", "인버스", "선물", "액티브", "ETN", "KODEX", "TIGER", "ACE","PLUS","SOL","RISE","KIWOOM","HANARO","1Q"]
    # 현재 날짜
    today = datetime.now().date()

    # 시가총액 계산 함수
    def get_market_cap(code):
        current_price = kiwoom.GetMasterLastPrice(code)  # 현재가
        listed_stocks = kiwoom.GetMasterListedStockCnt(code)  # 상장주식수
        market_cap = int(current_price) * int(listed_stocks)
        return market_cap

    # stock_list 테이블에 데이터 저장
    for code in code_list:
        # 종목 이름 가져오기
        name = kiwoom.GetMasterCodeName(code)

        C = 0
        for n in check_name:
            if n in name:
                C = 1
                break
        if C:
            continue

        if (name[len(name) - 1] == "우"):
            continue

        print(name, "정보 확인")
        time.sleep(1)

        # 시가총액 계산
        market_cap = get_market_cap(code)
        listed_date = kiwoom.GetMasterListedStockDate(code)
        if code in kospi_code_list:
            code += ".KS"
        else:
            code += ".KQ"
        if(cnt == 1): #시가총액 버튼만 누른경우
            if market_cap >= num1:
                print(name, "은 리스트에 들어옵니다")
                # stock_list 테이블에 데이터 삽입
                sql = f"""
                INSERT INTO {table_name} (code, name)
                VALUES (%s, %s)
                """
                cursor.execute(sql, (code, name))
                conn.commit()
        elif(cnt == 2): #상장일 수 버튼만 누른경우
            # 상장일 가져오기
            if (today - listed_date.date()) >= timedelta(days=num2):
                continue
            else:
                print(name, "은 리스트에 들어옵니다")
                # stock_list 테이블에 데이터 삽입
                sql = f"""
                                INSERT INTO {table_name} (code, name)
                                VALUES (%s, %s)
                                """
                cursor.execute(sql, (code, name))
                conn.commit()
        elif(cnt==3): # 두 버튼 모두 선택하였을 경우
            if market_cap >= num1:
                if (today - listed_date.date()) >= timedelta(days=num2):
                    continue

                print(name, "은 리스트에 들어옵니다")
                # stock_list 테이블에 데이터 삽입
                sql = f"""
                INSERT INTO {table_name} (code, name)
                VALUES (%s, %s)
                """
                cursor.execute(sql, (code, name))
                conn.commit()
        else: # 두 버튼 모두 선택 안하였을 경우
            print(name, "은 리스트에 들어옵니다")
            # stock_list 테이블에 데이터 삽입
            sql = f"""
                            INSERT INTO {table_name} (code, name)
                            VALUES (%s, %s)
                            """
            cursor.execute(sql, (code, name))
            conn.commit()

    # 연결 종료
    cursor.close()
    conn.close()

def storage_list_info(person_name,chat_id,RSI_value,BOL_value,SMA_value,RSI_1,BOL_1,SMA_1):
    # MySQL 연결
    conn = pymysql.connect(host='127.0.0.1', user='root', password='jun12160', db='stock', charset='utf8')
    cursor = conn.cursor()

    table_name = "users"
    cursor.execute(f"SELECT name FROM {table_name}")
    users = cursor.fetchall()  # 튜플 리스트 반환
    users = [name[0] for name in users]
    if person_name not in users:
        return

    table_name = "stock_info_list"

    sql = f"INSERT INTO `{table_name}` (name, chat_id, RSI_value, BOL_value, SMA_value, RSI_1, BOL_1, SMA_1) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(sql, (
        person_name,
        chat_id,
        RSI_value,
        BOL_value,
        SMA_value,
        RSI_1,
        BOL_1,
        SMA_1
    ))
    conn.commit()

    # 연결 종료
    cursor.close()
    conn.close()

# 텔레그램 메시지 전송 함수
def send_telegram_message(message,chat_id):
    # 텔레그램 봇 API 토큰
    BOT_TOKEN = "7728392458:AAFsJXgn__xEp-83Phdnan1-lKJne0bHfeg"
    CHAT_ID = chat_id  # 봇과 대화한 사용자의 채팅 ID
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print("텔레그램 메시지 전송 성공!")
    else:
        print(f"텔레그램 메시지 전송 실패: {response.status_code}, {response.text}")

def calculate(person_name,chat_id,RSI_value,BOL_value,SMA_value,RSI_1,BOL_1,SMA_1):
    # MySQL 연결
    conn = pymysql.connect(host='127.0.0.1', user='root', password='jun12160', db='stock', charset='utf8')
    cursor = conn.cursor()

    table_name = f"{person_name}_stock_list"
    # stock_list 테이블에서 종목 코드 읽어오기
    cursor.execute(f"SELECT code FROM {table_name}")
    stock_codes = cursor.fetchall()  # 튜플 리스트 반환
    stock_codes = [code[0] for code in stock_codes]

    cursor.execute(f"SELECT name FROM {table_name}")
    stock_names = cursor.fetchall()  # 튜플 리스트 반환
    stock_names = [name[0] for name in stock_names]

    # 텔레그램 시작 메세지
    today = datetime.now().date()
    message = f"{today}의 {person_name}의 주식 종목들을 확인중입니다."
    send_telegram_message(message, chat_id)

    for i in range(0,len(stock_codes)):
        code = stock_codes[i]
        name = stock_names[i]

        ticker = yf.Ticker(code)
        # 일봉 데이터
        df = ticker.history(period="1y")
        # 주봉 데이터
        df2 = ticker.history(period="2y", interval="1wk")

        rsi = -1
        bol = -1
        SMA = -1
        if(RSI_value):
            try:
                if(RSI_1 =="일봉"):
                    df['RSI'] = ta.rsi(df['Close'], length=14)
                    rsi = df['RSI'].iloc[-1]
                else:
                    df2['RSI'] = ta.rsi(df['Close'], length=14)
                    rsi = df2['RSI'].iloc[-1]
            except Exception:
                continue

            if rsi == None or rsi >= RSI_value:
                continue

            message = f"{name}의 rsi = {rsi} 매수 기회일 수 있습니다!"

        if (BOL_value):
            try:
                if (BOL_1 == "일봉"):
                    price = df['Close'].iloc[-1]
                    bbands = ta.bbands(df['Close'], length=40, stddev=2)
                    df['BB_Lower'] = bbands['BBL_40_2.0']  # 하단 밴드
                    bol = df['BB_Lower'].iloc[-1]
                else:
                    price = df2['Low'].iloc[-1]
                    bbands = ta.bbands(df2['Close'], length=40, stddev=2)
                    df2['BB_Lower'] = bbands['BBL_40_2.0']  # 하단 밴드
                    bol = df2['BB_Lower'].iloc[-1]
            except Exception:
                continue

            if bol == None or price > bol:
                continue

            message = f"{name}의 볼린저밴드 {BOL_1} 매수 기회일 수 있습니다!"

        if (SMA_value):
            try:
                if (SMA_1 == "일봉"):
                    price = df['Close'].iloc[-1]
                    df['SMA'] = ta.sma(df['Close'], length=120)
                    SMA = df['SMA'].iloc[-1]
                else:
                    price = df2['Close'].iloc[-1]
                    df2['SMA'] = ta.sma(df2['Close'], length=120)
                    SMA = df2['SMA'].iloc[-1]
            except Exception:
                continue

            if SMA == None or price > SMA:
                continue

            message = f"{name}의 이동평균선 매수 기회일 수 있습니다!"

        send_telegram_message(message,chat_id)  # 텔레그램으로 메시지 전송

    message = f"{today}의 {person_name}의 주식 종목들을 모두 확인하였습니다."
    send_telegram_message(message, chat_id)


    # 연결 종료
    cursor.close()
    conn.close()

def schedule_calculate():
    conn = pymysql.connect(host='127.0.0.1', user='root', password='jun12160', db='stock', charset='utf8')
    cursor = conn.cursor()

    cursor.execute("SELECT name, chat_id, RSI_value, BOL_value, SMA_value, RSI_1, BOL_1, SMA_1 FROM stock_info_list")
    rows = cursor.fetchall()

    for row in rows:
        calculate(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7])


def start_scheduler():
    scheduler = BackgroundScheduler()
    # 평일 18:00에 작업 실행
    trigger = CronTrigger(day_of_week='mon-fri',hour=18, minute=00)
    scheduler.add_job(schedule_calculate, trigger)
    scheduler.start()