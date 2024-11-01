import socket
import json
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog
import sys

# 서버 주소와 포트 설정
HOST = '192.168.0.12'
PORT = 25565

first = True

def receive_messages(s):
    while True:
        try:
            response = s.recv(1024).decode()  # 서버로부터 응답 받기
            if not response:
                print("서버와의 연결이 종료되었습니다.")
                break

            # 응답을 JSON으로 파싱
            response_data = json.loads(response)

            # MESSAGE_GET 값 추출 및 출력
            message_get = response_data.get("MESSAGE_GET")
            user_name = response_data.get('user_name')

            # GUI에 메시지 출력
            if response_data.get('color') == "red":
                text_area.insert(tk.END, f"{user_name}: {message_get}\n", "red")  # "red" 태그 사용
            else:
                text_area.insert(tk.END, f"{user_name}: {message_get}\n", "default")  # "default" 태그 사용

            text_area.see(tk.END)  # 스크롤을 맨 아래로 내림

        except json.JSONDecodeError:
            print("JSON 디코딩에 실패했습니다.")
        except Exception as e:
            print(f"오류 발생: {e}")
            break

def send_message():
    message = message_entry.get()
    if message.lower() == "exit":
        print("연결을 종료합니다.")
        sys.exit()

    # JSON 형식으로 데이터 변환 및 전송
    data = {
        "message": message,
        "user_name": name,
        "hash_value" : hash_value
    }

    # JSON으로 변환하여 전송
    s.sendall(json.dumps(data).encode())  # JSON 문자열을 인코딩하여 전송

    message_entry.delete(0, tk.END)  # 입력창 초기화

# 사용자 닉네임 입력
root = tk.Tk()
root.withdraw()  # 이 창을 숨김

name = simpledialog.askstring("닉네임 입력", "닉네임을 입력하세요:", parent=root)
hash_value = simpledialog.askstring("키 입력", "키를 입력하세요:", parent=root)

# 소켓 생성 및 서버 연결
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))  # 서버에 연결

# 입장 메시지 전송
def send_first():
    global first
    if first:
        message = f"{name}님이 입장하였습니다"
        data = {
            "message": message,
            "user_name": name,
            "hash_value": hash_value
        }
        s.sendall(json.dumps(data).encode())  # JSON 문자열을 인코딩하여 전송
        first = False

send_first()

# tkinter GUI 설정
root.deiconify()
root.title("Chat Client")

# 메시지 표시 영역
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD)
text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# 태그 설정: "red" 태그는 빨간색, "default" 태그는 기본 색상
text_area.tag_configure("red", foreground="red")
text_area.tag_configure("default", foreground="black")

# 메시지 입력창
message_entry = tk.Entry(root, width=50)
message_entry.pack(padx=10, pady=(0, 10), side=tk.LEFT, fill=tk.X, expand=True)

# 전송 버튼
send_button = tk.Button(root, text="전송", command=send_message)
send_button.pack(padx=(5, 10), pady=(0, 10), side=tk.RIGHT)

# 수신 메시지를 처리하는 스레드 시작 (text_area가 정의된 후에 실행)
thread = threading.Thread(target=receive_messages, args=(s,))
thread.daemon = True  # 메인 스레드 종료 시 함께 종료
thread.start()

# 메인 루프 실행
root.mainloop()

# 연결 종료
s.close()
sys.exit()
