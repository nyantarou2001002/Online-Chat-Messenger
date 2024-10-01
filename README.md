# Online Chat Messenger
クライアント-サーバー間のTCP通信によってチャットルームを作成し、UDP通信によって同じ部屋に参加しているユーザー同士でメッセージを送信できるプログラムです。
CLIから起動できます。

#使用方法
このリポジトリをクローンしてください。
ターミナルを起動しプロジェクトディレクトリ上に移動後、python3 server.pyでサーバー、別のタブでpython3 client.pyでクライアント を起動します。

![スクリーンショット 2024-10-01 10 19 07](https://github.com/user-attachments/assets/e39283ac-f54f-458f-be4d-4d9dee78f426)


![スクリーンショット 2024-10-01 10 19 25](https://github.com/user-attachments/assets/2332bd6e-691e-4357-a9b8-a208a9bcf167)

クライアントで１と入力後、ユーザー名と部屋名とパスワードを入力することで部屋を作成できます(作成したユーザーが部屋のホストとなります)
![スクリーンショット 2024-10-01 10 20 42](https://github.com/user-attachments/assets/6273be55-8ee2-4964-9cea-476455bac0a3)

別のターミナルタブから別のユーザーを、コマンド2で作成済みの部屋に入室させます。
![スクリーンショット 2024-10-01 10 21 12](https://github.com/user-attachments/assets/fe38526f-0c07-4ebb-ac77-536fc7c9a011)

メッセージを入力・送信すると、同じ部屋に入っている他のユーザーの画面から送信メッセージが確認できます。
![スクリーンショット 2024-10-01 10 21 45](https://github.com/user-attachments/assets/c12e62f0-2bb6-48b9-bfaf-47e5a6ec0097)
![スクリーンショット 2024-10-01 10 21 52](https://github.com/user-attachments/assets/4ff11430-d8b2-4c65-b36f-4603e4c575d4)

最後に/exitと入力するとルームから退出することができます。(ホストが退出すると自動的にルーム自体が閉じ、そのメッセージがルームの中にいるクライアントに送られます)
![スクリーンショット 2024-10-01 10 26 12](https://github.com/user-attachments/assets/632b35d3-c3d8-429c-84de-61e5162f25d1)

![スクリーンショット 2024-10-01 10 26 06](https://github.com/user-attachments/assets/47ec2b7f-e799-4028-9498-95b16402f351)

![スクリーンショット 2024-10-01 10 25 58](https://github.com/user-attachments/assets/3691564d-706c-4f0c-ace5-aa6dfa99f4d4)

