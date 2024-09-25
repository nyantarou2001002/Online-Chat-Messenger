import socket
import threading

def listen_for_messages(client_socket):
    while True:
        try:
            # サーバからのメッセージを受信
            data, _ = client_socket.recvfrom(4096)
            message = data.decode('utf-8')
            if message == "ルームが閉鎖されました":
                print("ルームが閉鎖されました。")
                break
            print(message)
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            break

# クライアントの設定
server_ip = '127.0.0.1'
server_port = 12345
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

username = input("ユーザー名を入力してください: ").strip()
print("ユーザー名の入力を受け付けました。会話をお楽しみください。")

# サーバからのメッセージを別スレッドで受信
listen_thread = threading.Thread(target=listen_for_messages, args=(client_socket,))
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
        client_socket.sendto(message_data, (server_ip, server_port))

        # ルーム閉鎖のコマンドが送られた場合
        if message.lower() == "exit":
            print("退出しました。")
            break

except Exception as e:
    print(f"エラーが発生しました: {e}")
