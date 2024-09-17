import socket
import select
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
        # 現在時刻を取得
        current_time = time.time()

        # 受信準備 (サーバソケットでデータが来るのを待つ)
        ready_sockets, _, _ = select.select([server_socket], [], [], 1)

        if ready_sockets:
            # メッセージ受信
            data, addr = server_socket.recvfrom(4096)

            # クライアントの最終メッセージ送信時刻を更新
            clients[addr] = current_time

            # 他の全クライアントに送信
            for client in list(clients.keys()):
                if client != addr:  # 自分には送信しない
                    server_socket.sendto(data, client)

        # 古いクライアントを削除（タイムアウトしたクライアント）
        clients = {addr: last_time for addr, last_time in clients.items() if current_time - last_time < timeout_seconds}

    except Exception as e:
        print(f"エラーが発生しました: {e}")
