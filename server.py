import socket
import threading
import time
import struct
import os

# サーバの設定
server_ip = '127.0.0.1'
tcp_port = 12345
udp_port = 12346

# クライアントのトークンとIPアドレスの管理
valid_tokens = {'client1_token1', 'client2_token'}
allowed_ips = {'127.0.0.1'}

clients = {}
timeout_seconds = 60  # 60秒間メッセージがなければクライアントを削除
host_addr = None  # ホストのアドレスを保存

# チャットルーム、クライアント、トークンを管理するデータ構造
chat_rooms = {}  # {room_name: {'host_token': token, 'clients': {token: (ip, port, username)}}}
token_to_room = {}  # {token: room_name}

def generate_token():
    return os.urandom(16).hex()  # 32文字の16進数トークン

print("サーバが起動しました...")

def verify_token_and_ip(data, addr):
    try:
        token = data.decode('utf-8').strip()

        # IPアドレスをチェック
        if addr[0] not in allowed_ips:
            print(f"許可されていないIPアドレス: {addr[0]}")
            return False

        # トークンをチェック
        if token not in valid_tokens:
            print(f"無効なトークン: {token}")
            return False

        # クライアントを登録
        clients[addr] = time.time()

        global host_addr
        if host_addr is None:
            host_addr = addr  # 最初に接続したクライアントをホストとして設定

        print(f"クライアントが参加しました: {addr}")
        return True
    except Exception as e:
        print(f"トークン/IP確認中にエラーが発生しました: {e}")
        return False

def handle_tcp_client(conn, addr):
    try:
        # データを受信
        data = conn.recv(32)
        if len(data) < 32:
            print(f"不正なヘッダーサイズ from {addr}")
            conn.close()
            return

        # ヘッダーを解析
        header = data[:32]
        RoomNameSize, Operation, State, OperationPayloadSize = struct.unpack('!BBB29s', header)
        OperationPayloadSize = int.from_bytes(OperationPayloadSize, 'big')

        # ボディを受信
        body_size = RoomNameSize + OperationPayloadSize
        body = conn.recv(body_size)
        if len(body) < body_size:
            print(f"不正なボディサイズ from {addr}")
            return

    except Exception as e:
        print(f"エラーが発生しました（TCPサーバ処理中）: {e}")

