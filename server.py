import socket
import threading
import time

# サーバーのホストとポートを設定
HOST = 'localhost'
PORT = 12345
BUFFER_SIZE = 4096

# クライアント情報を保持するためのリスト
clients = []

# メッセージを全クライアントにリレーする関数
def relay_message(message, sender_address):
    for client in clients:
        if client != sender_address:
            server_socket.sendto(message, client)

# クライアントの接続を処理する関数
def handle_client():
    while True:
        try:
            # メッセージを受信
            message, address = server_socket.recvfrom(BUFFER_SIZE)
            if address not in clients:
                clients.append(address)
            
            # メッセージをリレー
            relay_message(message, address)
        except:
            # 例外が発生した場合、クライアントをリストから削除
            if address in clients:
                clients.remove(address)

# サーバーのセットアップ
def start_server():
    print(f"サーバーは {HOST}:{PORT} で起動中...")
    while True:
        handle_client()

# サーバーソケットの作成
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))

# サーバーを別スレッドで実行
server_thread = threading.Thread(target=start_server)
server_thread.start()
