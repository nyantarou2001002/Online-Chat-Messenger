import socket
import select
import time

# サーバの設定
server_ip = '127.0.0.1'
server_port = 12345
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((server_ip, server_port))

# クライアントのトークンとIPアドレスの管理
valid_tokens = {'client1_token1', 'client2_token'}
allowed_ips = {'127.0.0.1'}

clients = {}
timeout_seconds = 60  # 60秒間メッセージがなければクライアントを削除
host_addr = None  # ホストのアドレスを保存

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

while True:
    try:
        # 現在時刻を取得
        current_time = time.time()

        # 受信準備 (サーバソケットでデータが来るのを待つ)
        ready_sockets, _, _ = select.select([server_socket], [], [], 1)

        if ready_sockets:
            # メッセージ受信
            data, addr = server_socket.recvfrom(4096)

            if addr not in clients:
                if not verify_token_and_ip(data, addr):
                    continue  # トークンやIPが無効なら処理を中断
                else:
                    # トークンが確認されたら「参加完了」メッセージを送信
                    server_socket.sendto("参加完了".encode('utf-8'), addr)
                    continue

            # クライアントの最終メッセージ送信時刻を更新
            clients[addr] = current_time

            # ホストが退出したか確認
            if addr == host_addr and data.decode('utf-8').strip().lower() == "exit":
                # ルームを閉鎖する
                print("ホストが退出しました。ルームを閉鎖します。")
                for client in list(clients.keys()):
                    if client != host_addr:
                        server_socket.sendto("ルームが閉鎖されました".encode('utf-8'), client)
                break  # サーバーを終了

            # 他の全クライアントに送信
            for client in list(clients.keys()):
                if client != addr:  # 自分には送信しない
                    server_socket.sendto(data, client)

        # 古いクライアントを削除（タイムアウトしたクライアント）
        clients = {addr: last_time for addr, last_time in clients.items() if current_time - last_time < timeout_seconds}

    except Exception as e:
        print(f"エラーが発生しました: {e}")
