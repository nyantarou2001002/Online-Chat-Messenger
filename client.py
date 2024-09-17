import socket

# サーバの設定
server_ip = '127.0.0.1'
server_port = 12345
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# ユーザー名の入力
username = input("ユーザー名を入力してください: ")

while True:
    # メッセージの入力
    message = input("メッセージを入力してください: ")

    # ユーザー名の長さを1バイトで表現し、ユーザー名とメッセージを送信
    usernamelen = len(username.encode('utf-8'))
    data = usernamelen.to_bytes(1, 'big') + username.encode('utf-8') + message.encode('utf-8')
    client_socket.sendto(data, (server_ip, server_port))

    # サーバからの応答を受信
    response, _ = client_socket.recvfrom(4096)
    print(response.decode('utf-8'))
