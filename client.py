import socket
import threading

# サーバーのホストとポートを設定
HOST = 'localhost'
PORT = 12345
BUFFER_SIZE = 4096

# サーバーからのメッセージを受信する関数
def receive_messages():
    while True:
        try:
            message, _ = client_socket.recvfrom(BUFFER_SIZE)
            print(message.decode('utf-8'))
        except:
            print("メッセージの受信中にエラーが発生しました。")
            break

# クライアントのセットアップ
def start_client():
    username = input("ユーザー名を入力してください: ")
    while True:
        message = input("メッセージを入力してください: ")
        if message:
            # メッセージのフォーマット: [ユーザー名長さ (1バイト)] + [ユーザー名] + [メッセージ]
            username_len = len(username.encode('utf-8'))
            formatted_message = bytes([username_len]) + username.encode('utf-8') + message.encode('utf-8')
            client_socket.sendto(formatted_message, (HOST, PORT))

# クライアントソケットの作成
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# メッセージ受信用のスレッドを開始
receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

# クライアントを起動してサーバに接続
start_client()
