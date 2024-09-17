import socket
import time

# サーバの設定
server_ip = '127.0.0.1'
server_port = 12345
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((server_ip, server_port))

clients = {}
timeout_seconds = 60  # 60秒間メッセージがなければクライアントを削除

print("サーバが起動しました...")

while True:
    try:
        # 現在の時刻を取得
        current_time = time.time()

        # 古いクライアントをリストから削除
        clients = {addr: last_time for addr, last_time in clients.items() if current_time - last_time < timeout_seconds}

        # メッセージ受信
        data, addr = server_socket.recvfrom(4096)

        # クライアントの最終メッセージ送信時刻を更新
        clients[addr] = current_time

        # usernamelen の取得
        usernamelen = data[0]
        
        # 受け取ったデータをフォーマットして他のクライアントに転送
        username = data[1:usernamelen+1].decode('utf-8')  # ユーザー名部分
        message = data[usernamelen+1:].decode('utf-8')    # メッセージ部分
        formatted_message = f"{username} : {message}".encode('utf-8')

        # 各クライアントに送信
        for client in clients.keys():
            if client != addr:  # 自分には送信しない
                server_socket.sendto(formatted_message, client)

    except Exception as e:
        print(f"エラーが発生しました: {e}")
