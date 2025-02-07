import socket
import threading
import os

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 12345)

nickname = input("Enter your nickname: ")
groupchat = input("Enter Room ID you want to enter: ")

client_socket.sendto(f"JOIN:{nickname}:{groupchat}".encode(), server_address)

def receive_messages():
    while True:
        try:
            data, _ = client_socket.recvfrom(4096)
            message = data.decode()

            if message.startswith("SEND_FILE:"):
                _, sender, filename = message.split(":")
                print(f"File request received from {sender} for {filename}")
                send_file(sender, filename)

            else:
                print(message)

        except:
            break

def send_file(target_user, filename):
    if not os.path.exists(filename):
        print(f"File {filename} not found.")
        return

    with open(filename, "rb") as f:
        file_data = f.read()

    chunk_size = 1024
    total_chunks = (len(file_data) // chunk_size) + 1

    for i in range(total_chunks):
        chunk = file_data[i * chunk_size: (i + 1) * chunk_size]
        client_socket.sendto(f"FILE:{nickname}:{filename}:{total_chunks}:{i}:{chunk.decode()}".encode(), server_address)

def request_file(target_user, filename):
    client_socket.sendto(f"REQUEST_FILE:{nickname}:{target_user}:{filename}".encode(), server_address)

receive_thread = threading.Thread(target=receive_messages, daemon=True)
receive_thread.start()

while True:
    message = input()

    if message.lower() == "exit":
        client_socket.sendto(f"EXIT:{nickname}".encode(), server_address)
        break

    elif message.startswith("sendfile"):
        _, target, filename = message.split(" ", 2)
        send_file(target, filename)

    elif message.startswith("getfile"):
        _, target, filename = message.split(" ", 2)
        request_file(target, filename)

    else:
        client_socket.sendto(f"{nickname}: {message}".encode(), server_address)

client_socket.close()
print("Exiting from the group")
