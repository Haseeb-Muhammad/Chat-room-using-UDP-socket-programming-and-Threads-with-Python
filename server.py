import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('localhost', 12345))

print("Server is listening on localhost:12345")

clients = {}  # Dictionary to store clients as {nickname: address}

while True:
    data, client_address = server_socket.recvfrom(4096)
    message = data.decode()

    if message.startswith("REGISTER:"):
        nickname = message.split(":")[1]
        clients[nickname] = client_address
        print(f"Registered {nickname} at {client_address}")

    elif message.startswith("EXIT:"):
        nickname = message.split(":")[1]
        if nickname in clients:
            del clients[nickname]
        print(f"{nickname} left the chat.")

    elif message.startswith("UNICAST:"):
        _, sender, msg = message.split(":", 2)
        target_nickname, actual_message = msg.split(" ", 1)

        target_nickname = target_nickname.lstrip("@")
        if target_nickname in clients:
            target_address = clients[target_nickname]
            server_socket.sendto(f"(Private) {sender}: {actual_message}".encode(), target_address)
        else:
            server_socket.sendto(f"User {target_nickname} not found!".encode(), clients[sender])

    elif message.startswith("BROADCAST:"):
        _, sender, msg = message.split(":", 2)
        for nickname, address in clients.items():
            if nickname != sender:
                server_socket.sendto(f"{sender}: {msg}".encode(), address)

    elif message.startswith("FILE:"):  # Handle file transfer
        _, sender, recipient, filename, chunk_index, total_chunks, file_data = message.split(":", 6)
        if recipient in clients:
            recipient_address = clients[recipient]
            forward_message = f"FILE:{sender}:{filename}:{chunk_index}:{total_chunks}:{file_data}"
            server_socket.sendto(forward_message.encode(), recipient_address)
        else:
            server_socket.sendto(f"User {recipient} not found!".encode(), clients[sender])

    elif message.startswith("REQUEST_FILE:"):  # Handle file requests
        _, requester, target, filename = message.split(":")
        if target in clients:
            target_address = clients[target]
            server_socket.sendto(f"REQUEST_FILE:{requester}:{filename}".encode(), target_address)
        else:
            server_socket.sendto(f"User {target} not found!".encode(), clients[requester])
