import socket
import json
import threading
import sys
import hashlib
import secrets

# 랜덤 바이트 생성
random_bytes = secrets.token_bytes(32)  # 32 바이트 랜덤 값 생성

# SHA-256 해시 생성
hash_value = hashlib.sha256(random_bytes).hexdigest()
print("랜덤 해시 값:", hash_value)

# 서버 주소와 포트 설정
data = 'setting.json'

def read_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    
setting = read_json(data)

# 설정 파일에서 IP와 포트를 읽어옴
print(f"{setting['ip']}")

if not f"{setting['ip']}".count(".") == 3:
    print("IP 형식이 정상적이지 않습니다.")
    input()
    sys.exit()

HOST = setting["ip"]  # 로컬 호스트 (자신의 컴퓨터 IP)
PORT = setting["port"]  # 사용할 포트

clients = []  # 모든 클라이언트 연결을 저장하는 리스트
addd = None   # 차단된 클라이언트의 주소 저장

def handle_client(conn, addr):
    print(f"클라이언트 연결됨: {addr}")
    clients.append(conn)  # 새로운 클라이언트를 리스트에 추가
    with conn:
        while True:
            try:
                data = conn.recv(1024)  # 클라이언트로부터 데이터 수신
                if not data:
                    print(f"클라이언트 {addr}의 연결이 종료되었습니다.")
                    break

                # 데이터가 비어 있지 않은 경우에만 JSON으로 변환
                if data:
                    try:
                        message = json.loads(data.decode('utf-8'))  # 데이터 디코딩
                    except (UnicodeDecodeError, json.JSONDecodeError) as e:
                        print(f"데이터 디코딩 또는 JSON 변환 오류: {e}")
                        continue  # 오류 발생 시 다음 루프로 넘어감

                    print(f"받은 JSON 데이터: {message}")

                    # 해시값 검증 후 메시지 브로드캐스트
                    if message.get("hash_value") != hash_value:
                        print(f"잘못된 해시 값을 가진 클라이언트 {addr} 연결을 종료합니다.")
                        global addd
                        addd = addr  # 차단된 클라이언트 주소 저장
                        broadcast_message(message)
                        conn.sendall(json.dumps({
                            "status": "error",
                            "message": "Invalid hash value. Disconnecting...",
                            "color": "red"
                        }).encode('utf-8'))
                        conn.close()  # 연결 강제 종료
                        break

                    # 해시가 유효할 경우 메시지 브로드캐스트
                    broadcast_message(message)

            except ConnectionResetError:
                print(f"클라이언트 {addr}의 연결이 비정상적으로 종료되었습니다.")
                break

    # 연결 종료 시 클라이언트 리스트에서 제거
    clients.remove(conn)
    print(f"클라이언트 {addr} 연결 종료됨.")

def broadcast_message(message):
    # 응답을 JSON 형식으로 작성하여 모든 클라이언트에 전송
    if message.get("hash_value") == hash_value:
        response = {
            "status": "success",
            "message": "Data received",
            "MESSAGE_GET": message.get("message", "No message provided"),
            "user_name": message.get("user_name", "ERROR"),
            "color": "default"
        }
    else:
        response = {
            "status": "success",
            "message": "Data received",
            "MESSAGE_GET": f"잘못된 해시 값을 가진 클라이언트 {addd}의 연결을 차단 하였습니다.\n서버의 IP가 노출 되었을 수 있습니다.",
            "user_name": "server",
            "color": "red"
        }

    # 모든 클라이언트에 메시지 전송
    for client in clients:
        try:
            client.sendall(json.dumps(response).encode('utf-8'))
        except Exception as e:
            print(f"클라이언트로 메시지 전송 중 오류 발생: {e}")

# 소켓 생성 및 바인딩
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("서버가 시작되었습니다. 클라이언트의 연결을 기다리고 있습니다.")

    while True:  # 새로운 클라이언트 연결을 계속 대기
        conn, addr = s.accept()
        # 각 클라이언트를 위한 새로운 스레드 시작
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.start()

        print("새로운 클라이언트의 연결을 기다리고 있습니다...")
