import socket
import threading

def protocol_header(room_name, operation, state, payload):
    if len(payload.encode("utf-8")) < 29:
        payload = payload.ljust(29, " ")

    return len(room_name).to_bytes(1, 'big') +\
        operation.to_bytes(1, 'big') +\
        state.to_bytes(1, 'big') +\
        payload.encode('utf-8')
        

def listen_for_messages(udp_socket):
    while True:
        try:
            # サーバからのメッセージを受信
            data, _ = udp_socket.recvfrom(4096)
            print(data.decode('utf-8'))
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            break

# クライアントの設定
server_ip = '127.0.0.1'
server_port = 12345

client_ip = 'localhost'
client_port = 54321

# サーバーとの接続
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# サーバーとの接続を保証
try:
    tcp_socket.connect((server_ip, server_port))
except socket.error as err:
    print(err)

# ユーザー名を取得
username = input("ユーザー名を入力してください: ").strip()
# オペレーションを取得
operation = int(input('１又は２を選択してください (1:ルーム作成 2:ルームに参加): '))
# オペレーションを元にルーム名を取得
if(operation == 1):
    roomname = input('ルーム名を入力してください: ').strip()
else:
    roomname = ''
# 初期の操作コードは０
state = 0

# サーバーにヘッダーを送信
tcp_socket.send(protocol_header(roomname, operation, state, username))
print("ユーザーの入力を受け付けました。会話をお楽しみください。")

# サーバからのメッセージを別スレッドで受信
listen_thread = threading.Thread(target=listen_for_messages, args=(udp_socket,))
listen_thread.daemon = True  # メインスレッドが終了するときに自動的に終了する
listen_thread.start()

try:
    while True:
        # ユーザー名とメッセージを適切にフォーマットして送信
        message = input().strip()
        if not message:
            continue
        
        formatted_message = f"{username} : {message}"
        message_data = formatted_message.encode('utf-8')
        udp_socket.sendto(message_data, (server_ip, server_port))

except Exception as e:
    print(f"エラーが発生しました: {e}")
