import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('localhost', 12345))

print("Server is listening on localhost:12345")

client_list = set()

while True:
    data, client_address = server_socket.recvfrom(4096)
    
    # Add new clients to the list
    if client_address not in client_list:
        client_list.add(client_address)

    message = data.decode()
    print(f"Message received from {client_address}: {message}")

    if message.lower() == "exit":
        client_list.remove(client_address)
        continue

    # Send the message to all clients except the sender
    for client in client_list:
        if client != client_address:
            server_socket.sendto(data, client)
