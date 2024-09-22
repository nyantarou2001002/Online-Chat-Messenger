import socket
import select
import time

# サーバの設定
server_ip = '127.0.0.1'
server_port = 12345

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

clients = {}
timeout_seconds = 60  # 60秒間メッセージがなければクライアントを削除

udp_socket.bind((server_ip, server_port))
tcp_socket.bind((server_ip, server_port))
print("サーバが起動しました...")

while True:
    try:
        tcp_socket.listen()
        connection, client_address = tcp_socket.accept()

        # クライアントかヘッダーを受信する
        header = connection.recv(32)
        
        room_name_size = int.from_bytes(header[:1], "big")
        operation = int.from_bytes(header[1:2], "big")
        state = int.from_bytes(header[2:3], "big")
        payload_size = int.from_bytes(header[3:32], "big")

        print("------------------------------")
        print("Recive header from client.")
        print("room_name_size: ", room_name_size)
        print("operation: ", operation)
        print("state: ", state)
        print("payload_size: ", payload_size)
        print("------------------------------")

        # 現在時刻を取得
        current_time = time.time()

        # 受信準備 (サーバソケットでデータが来るのを待つ)
        ready_sockets, _, _ = select.select([tcp_socket], [], [], 1)

        if ready_sockets:
            # メッセージ受信
            data, addr = tcp_socket.recvfrom(4096)

            # クライアントの最終メッセージ送信時刻を更新
            clients[addr] = current_time

            # 他の全クライアントに送信
            for client in list(clients.keys()):
                if client != addr:  # 自分には送信しない
                    tcp_socket.sendto(data, client)

        # 古いクライアントを削除（タイムアウトしたクライアント）
        clients = {addr: last_time for addr, last_time in clients.items() if current_time - last_time < timeout_seconds}

    except Exception as e:
        print(f"エラーが発生しました: {e}")
