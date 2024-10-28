import socket
import json
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog

# 서버 주소와 포트 설정
HOST = '192.168.0.12'
PORT = 25565

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
            text_area.insert(tk.END, f"{user_name}: {message_get}\n")
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
        root.quit()

    # JSON 형식으로 데이터 변환 및 전송
    data = {
        "message": message,
        "user_name": name
    }

    # JSON으로 변환하여 전송
    s.sendall(json.dumps(data).encode())  # JSON 문자열을 인코딩하여 전송

    message_entry.delete(0, tk.END)  # 입력창 초기화

# 사용자 닉네임 입력
name = simpledialog.askstring("닉네임 입력", "닉네임을 입력하세요:", parent=tk.Tk())

# 소켓 생성 및 서버 연결
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))  # 서버에 연결

# 수신 메시지를 처리하는 스레드 시작
thread = threading.Thread(target=receive_messages, args=(s,))
thread.daemon = True  # 메인 스레드 종료 시 함께 종료
thread.start()

# tkinter GUI 설정
root = tk.Tk()
root.title("Chat Client")

# 메시지 표시 영역
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD)
text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# 메시지 입력창
message_entry = tk.Entry(root, width=50)
message_entry.pack(padx=10, pady=(0, 10), side=tk.LEFT, fill=tk.X, expand=True)

# 전송 버튼
send_button = tk.Button(root, text="전송", command=send_message)
send_button.pack(padx=(5, 10), pady=(0, 10), side=tk.RIGHT)

# 메인 루프 실행
root.mainloop()

# 연결 종료
s.close()
