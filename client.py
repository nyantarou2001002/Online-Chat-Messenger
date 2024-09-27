import socket
import threading
import struct

def listen_for_messages(client_socket):
    while True:
        try:
            # サーバからのメッセージを受信
            data, _ = client_socket.recvfrom(4096)
            print(data.decode('utf-8'))
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            break

# クライアントの設定
server_ip = '127.0.0.1'
tcp_port = 12345
udp_port = 12346

# ユーザーに操作を選択させる
while True:
    print("1: チャットルームを作成")
    print("2: チャットルームに参加")
    choice = input("操作を選択してください (1または2): ").strip()
    if choice in ('1', '2'):
        break
    else:
        print("無効な入力です。もう一度入力してください。")

username = input("ユーザー名を入力してください: ").strip()
room_name = input("ルーム名を入力してください: ").strip()

# TCP接続を確立
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.connect((server_ip, tcp_port))

# TCRPプロトコルに従ってリクエストを送信
RoomNameSize = len(room_name.encode('utf-8'))
Operation = int(choice)
State = 0  # リクエスト
username_bytes = username.encode('utf-8')
OperationPayloadSize = len(username_bytes)
header = struct.pack('!BBB29s', RoomNameSize, Operation, State, OperationPayloadSize.to_bytes(29, 'big'))
body = room_name.encode('utf-8') + username_bytes
tcp_socket.sendall(header + body)

# 状態1の応答を受信
response = tcp_socket.recv(32)
resp_RoomNameSize, resp_Operation, resp_State, resp_PayloadSize = struct.unpack('!BBB29s', response)
if resp_State != 1:
    print("サーバからの無効な応答")
    tcp_socket.close()
    exit()

# 状態2の応答を受信
response = tcp_socket.recv(32 + 255)
resp_RoomNameSize, resp_Operation, resp_State, resp_PayloadSize = struct.unpack('!BBB29s', response[:32])
if resp_State != 2:
    print("サーバからの無効な応答")
    tcp_socket.close()
    exit()

token_bytes = response[32:32+255].rstrip(b'\x00')
token = token_bytes.decode('utf-8')

print("サーバとの接続が確立されました。チャットを開始します。")

tcp_socket.close()

# UDPソケットを作成し、ローカルアドレスにバインド
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind(('', 0))  # OSにポートを選択させる
client_port = udp_socket.getsockname()[1]
print(f"クライアントのUDPポートは {client_port} です")

# サーバからのメッセージを別スレッドで受信
listen_thread = threading.Thread(target=listen_for_messages, args=(udp_socket,))
listen_thread.daemon = True  # メインスレッドが終了するときに自動的に終了する
listen_thread.start()

# 初回に「ユーザー名がルーム名に参加しました。」というメッセージを送信
join_message = f"{username}が{room_name}に参加しました。"
room_name_bytes = room_name.encode('utf-8')
token_bytes = token.encode('utf-8')
message_bytes = join_message.encode('utf-8')
RoomNameSize = len(room_name_bytes)
TokenSize = len(token_bytes)
header = struct.pack('!BB', RoomNameSize, TokenSize)
packet = header + room_name_bytes + token_bytes + message_bytes
udp_socket.sendto(packet, (server_ip, udp_port))

try:
    while True:
        # ユーザーからの入力を取得
        message = input().strip()
        if not message:
            continue

        # メッセージを適切にフォーマットして送信
        room_name_bytes = room_name.encode('utf-8')
        token_bytes = token.encode('utf-8')
        RoomNameSize = len(room_name_bytes)
        TokenSize = len(token_bytes)
        header = struct.pack('!BB', RoomNameSize, TokenSize)
        packet = header + room_name_bytes + token_bytes + message.encode('utf-8')
        udp_socket.sendto(packet, (server_ip, udp_port))

except Exception as e:
    print(f"エラーが発生しました: {e}")
