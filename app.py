from threading import Thread
from flask import Flask, render_template, request, jsonify
from list import create_table,reset_table, make_list,calculate, storage_list_info,start_scheduler
from pykiwoom.kiwoom import Kiwoom
from PyQt5.QtWidgets import QApplication
import requests
import sys

app = Flask(__name__)

kiwoom = None
siga_value , day_value = 0 ,0
RSI_value,BOL_value,SMA_value = 0,0,0
RSI_1,BOL_1,SMA_1 = "","",""
person_name = ""
chat_id = ""
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        global kiwoom,siga_value, day_value, person_name,chat_id,RSI_value,BOL_value,SMA_value,RSI_1,BOL_1,SMA_1
        # 기술적 지표 폼 데이터 처리
        # 종목 제한 폼 데이터 처리 (추가 버튼)
        if 'add_filter1' in request.form:
            indicator = request.form['indicator']
            bong = request.form['day_week']
            lower_value = request.form['lower_value']
            print(f"기술적 지표: {indicator},봉:{bong}, 하단 수치: {lower_value}")
            # 여기에 추가 버튼을 눌렀을 때의 로직을 구현합니다.
            if(indicator == "RSI"):
                RSI_1 = bong
                RSI_value = int(lower_value)
            elif(indicator == "볼린저밴드"):
                BOL_1 = bong
                BOL_value = int(lower_value)
            elif(indicator == "이동평균선"):
                SMA_1 = bong
                SMA_value = int(lower_value)

        if 'technical_submit' in request.form:
            print(f"기술적 지표의 확인버튼을 눌렀습니다.")
            storage_list_info(person_name, chat_id, RSI_value, BOL_value, SMA_value, RSI_1, BOL_1, SMA_1)
            #calculate(person_name, chat_id, RSI_value, BOL_value, SMA_value, RSI_1, BOL_1, SMA_1)
            RSI_value, BOL_value, SMA_value = 0, 0, 0
            RSI_1, BOL_1, SMA_1 = "", "", ""

        # 종목 제한 폼 데이터 처리 (추가 버튼)
        elif 'add_filter2' in request.form:
            filter_type = request.form['filter_type']
            filter_value = request.form['filter_value']
            print(f"종목 제한 추가: {filter_type}, 값: {filter_value}")
            # 여기에 추가 버튼을 눌렀을 때의 로직을 구현합니다.
            if (filter_type == "시가총액"):
                siga_value = int(filter_value)
            elif(filter_type == "상장 일수"):
                day_value = int(filter_value)
        # 종목 제한 폼 데이터 처리
        elif 'filter_submit' in request.form:
            print(f"종목제한의 확인버튼을 눌렀습니다.")

            login()

            # 여기에 종목 제한 함수를 호출하는 로직을 추가
            if(siga_value!=0 and day_value!=0):
                make_list(3,person_name,siga_value,day_value,kiwoom)
            elif(siga_value!=0):
                make_list(1, person_name, siga_value, day_value,kiwoom)
            elif(day_value!=0):
                make_list(2, person_name, siga_value, day_value,kiwoom)
            else:
                make_list(0, person_name, siga_value, day_value,kiwoom)

            siga_value, day_value = 0, 0

        # 이름 폼 데이터 처리
        elif 'name_submit' in request.form:
            person_name = request.form['name']
            chat_id = request.form['CHAT_ID']
            print(f"이름: {person_name}, 챗아이디: {chat_id}")
            # 여기에 이름 처리 함수를 호출하는 로직을 추가
            create_table(person_name)

        elif 'reset_submit' in request.form:
            temp_name = request.form['name']
            temp_chat_id = request.form['CHAT_ID']
            print(f"{temp_name}_stock_list를 초기화합니다.")
            # 여기에 이름 처리 함수를 호출하는 로직을 추가
            reset_table(temp_name)

    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    global kiwoom  # Kiwoom 객체를 사용
    if kiwoom is None:
        return jsonify({"status": "Kiwoom instance not initialized"}), 500

    try:
        # 로그인 요청
        kiwoom.CommConnect()
        return jsonify({"status": "Login request sent"})  # 요청이 성공적으로 전송되었음을 반환
    except Exception as e:
        return jsonify({"status": f"Error occurred: {str(e)}"}), 500

@app.route("/get_chat_id")
def get_chat_id():
    TOKEN = "7728392458:AAFsJXgn__xEp-83Phdnan1-lKJne0bHfeg"
    URL = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

    response = requests.get(URL)
    data = response.json()

    if "result" in data and len(data["result"]) > 0:
        chat_id = data["result"][0]["message"]["chat"]["id"]
        print(chat_id)
        return jsonify({"chat_id": chat_id})
    else:
        print("봇에게 채팅을 보내지 않음")
        return jsonify({"error" : "먼저 봇에게 채팅을 보내세요"})

def run_flask_app():
    app.run(host="0.0.0.0", port=5000,debug=True, use_reloader=False)  # `use_reloader=False`로 재시작 방지
def run_kiwoom_app():
    global kiwoom
    app = QApplication(sys.argv)  # PyQt5 앱 생성
    kiwoom = Kiwoom()  # Kiwoom 객체 생성
    app.exec_()  # PyQt5 이벤트 루프 실행

if __name__ == '__main__':
    start_scheduler()

    # Flask를 별도의 스레드에서 실행
    t_flask = Thread(target=run_flask_app, daemon=True)
    t_flask.start()

    # PyQt5를 메인 스레드에서 실행
    run_kiwoom_app()



