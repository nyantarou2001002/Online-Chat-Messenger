import socket
import threading
import time
import struct
import os
import json

# サーバの設定
server_ip = '127.0.0.1'
tcp_port = 12345
udp_port = 12346

# チャットルーム、クライアント、トークンを管理するデータ構造
chat_rooms = {}  # {room_name: {'host_token': token, 'clients': {token: (ip, port, username)}, 'password': password}}
token_to_room = {}  # {token: room_name}

# ロックオブジェクトを作成（スレッド間のデータ競合を防ぐため）
lock = threading.Lock()

def generate_token():
    return os.urandom(16).hex()  # 32文字の16進数トークン

print("サーバが起動しました...")

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
            conn.close()
            return

        room_name_bytes = body[:RoomNameSize]
        room_name = room_name_bytes.decode('utf-8')
        operation_payload = body[RoomNameSize:]

        # OperationPayloadをJSONとしてデコード
        operation_payload_json = operation_payload.decode('utf-8')
        payload_dict = json.loads(operation_payload_json)
        username = payload_dict.get('username')
        password = payload_dict.get('password')

        # 操作の処理
        if Operation == 1:  # チャットルーム作成
            with lock:
                if room_name in chat_rooms:
                    # ルームが既に存在する場合、エラーを返す
                    status_code = 1  # エラーコード
                    # 状態1の応答を送信
                    response_header = struct.pack('!BBB29s', RoomNameSize, Operation, 1, b'\x00'*29)
                    conn.sendall(response_header)
                    conn.close()
                    return
                else:
                    # ルームを作成
                    token = generate_token()
                    chat_rooms[room_name] = {
                        'host_token': token,
                        'clients': {token: (addr[0], None, username)},
                        'password': password  # パスワードを保存
                    }
                    token_to_room[token] = room_name

            # 状態1の応答を送信（成功）
            status_code = 0  # 成功コード
            response_header = struct.pack('!BBB29s', RoomNameSize, Operation, 1, b'\x00'*29)
            conn.sendall(response_header)

            # 状態2でトークンを送信
            token_bytes = token.encode('utf-8')
            response_header = struct.pack('!BBB29s', RoomNameSize, Operation, 2, b'\x00'*29)
            response_body = token_bytes.ljust(255, b'\x00')  # トークンは最大255バイト
            conn.sendall(response_header + response_body[:255])
            conn.close()
            print(f"チャットルーム '{room_name}' が作成されました。ホスト: {username}")
            return
        elif Operation == 2:  # チャットルームに参加
            with lock:
                if room_name not in chat_rooms:
                    # ルームが存在しない場合、エラーを返す
                    status_code = 1  # エラーコード
                    response_header = struct.pack('!BBB29s', RoomNameSize, Operation, 1, b'\x00'*29)
                    conn.sendall(response_header)
                    conn.close()
                    return
                else:
                    # パスワードの検証
                    room_password = chat_rooms[room_name]['password']
                    if room_password != password:
                        # パスワードが一致しない場合、エラーを返す
                        status_code = 1  # エラーコード
                        response_header = struct.pack('!BBB29s', RoomNameSize, Operation, 1, b'\x00'*29)
                        conn.sendall(response_header)
                        conn.close()
                        print(f"ユーザー '{username}' がチャットルーム '{room_name}' への参加に失敗しました（パスワード不一致）。")
                        return
                    # クライアントをルームに追加
                    token = generate_token()
                    chat_rooms[room_name]['clients'][token] = (addr[0], None, username)
                    token_to_room[token] = room_name

            # 状態1の応答を送信（成功）
            status_code = 0  # 成功コード
            response_header = struct.pack('!BBB29s', RoomNameSize, Operation, 1, b'\x00'*29)
            conn.sendall(response_header)

            # 状態2でトークンを送信
            token_bytes = token.encode('utf-8')
            response_header = struct.pack('!BBB29s', RoomNameSize, Operation, 2, b'\x00'*29)
            response_body = token_bytes.ljust(255, b'\x00')  # トークンは最大255バイト
            conn.sendall(response_header + response_body[:255])
            conn.close()
            print(f"ユーザー '{username}' がチャットルーム '{room_name}' に参加しました。")
            return
        else:
            # 未知の操作コード
            print(f"未知の操作コード: {Operation}")
            conn.close()
            return

    except Exception as e:
        print(f"エラーが発生しました（TCPクライアント処理中）: {e}")
        conn.close()

# TCPサーバーを開始
tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_server_socket.bind((server_ip, tcp_port))
tcp_server_socket.listen(5)

def tcp_server():
    print("TCPサーバが起動しました...")
    while True:
        conn, addr = tcp_server_socket.accept()
        threading.Thread(target=handle_tcp_client, args=(conn, addr)).start()

# UDPサーバーを開始
udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_server_socket.bind((server_ip, udp_port))

def udp_server():
    print("UDPサーバが起動しました...")
    while True:
        try:
            data, addr = udp_server_socket.recvfrom(4096)
            if len(data) < 3:
                continue
            # ヘッダーを解析
            RoomNameSize = data[0]
            TokenSize = data[1]
            MessageType = data[2]
            header_size = 3
            body = data[header_size:]

            # ルーム名とトークンを取得
            room_name_bytes = body[:RoomNameSize]
            token_bytes = body[RoomNameSize:RoomNameSize+TokenSize]
            message = body[RoomNameSize+TokenSize:]

            room_name = room_name_bytes.decode('utf-8')
            token = token_bytes.decode('utf-8')

            with lock:
                if token not in token_to_room or token_to_room[token] != room_name:
                    # トークンが無効
                    print(f"無効なトークン from {addr}")
                    continue

                # クライアント情報を取得
                client_info = chat_rooms[room_name]['clients'].get(token)
                if not client_info:
                    print(f"クライアント情報が見つかりません for token {token}")
                    continue

                # クライアントのIPアドレスの検証
                if client_info[0] != addr[0]:
                    print(f"IPアドレスが一致しません for token {token}")
                    continue

                # クライアントのUDPポートを更新
                if client_info[1] != addr[1]:
                    client_info = (addr[0], addr[1], client_info[2])
                    chat_rooms[room_name]['clients'][token] = client_info

                username = client_info[2]

                if MessageType == 1:  # 切断メッセージ
                    # クライアントをルームから削除
                    del chat_rooms[room_name]['clients'][token]
                    del token_to_room[token]
                    # クライアントに切断確認を送信（オプション）
                    disconnect_message = b'\x01' + 'サーバから切断されました。'.encode('utf-8')

                    udp_server_socket.sendto(disconnect_message, addr)
                    print(f"ユーザー '{username}' がチャットルーム '{room_name}' から切断しました。")

                    # ホストが切断した場合、ルームを閉じる
                    if token == chat_rooms[room_name]['host_token']:
                        # 他のクライアントにルームが閉じられたことを通知
                        notification = b'\x01' + f"ホストが退出したため、チャットルーム '{room_name}' は閉じられました。".encode('utf-8')
                        for client_token, (client_ip, client_port, _) in chat_rooms[room_name]['clients'].items():
                            if client_port is not None:
                                udp_server_socket.sendto(notification, (client_ip, client_port))
                        # ルームを削除
                        del chat_rooms[room_name]
                        print(f"チャットルーム '{room_name}' が閉じられました。")
                    continue

                if message:
                    formatted_message = f"{username} : {message.decode('utf-8')}"
                else:
                    # メッセージが空の場合はスキップ
                    continue

                # ルーム内の他のクライアントにメッセージを送信
                for client_token, (client_ip, client_port, _) in chat_rooms[room_name]['clients'].items():
                    if client_token != token:
                        if client_port is not None:
                            # 通常のメッセージは MessageType = 0
                            packet = b'\x00' + formatted_message.encode('utf-8')
                            udp_server_socket.sendto(packet, (client_ip, client_port))

        except Exception as e:
            print(f"エラーが発生しました（UDPサーバ処理中）: {e}")
            continue

# TCPとUDPサーバーを別スレッドで起動
tcp_thread = threading.Thread(target=tcp_server)
tcp_thread.daemon = True
tcp_thread.start()

udp_thread = threading.Thread(target=udp_server)
udp_thread.daemon = True
udp_thread.start()

# メインスレッドを維持
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("サーバを終了します...")
