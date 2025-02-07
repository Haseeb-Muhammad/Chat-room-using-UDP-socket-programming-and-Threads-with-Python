import socket
import threading

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('localhost', 12345))

print("Server is listening on localhost:12345")

clients = {}  # Stores {username: (address, room_id)}
rooms = {}  # Stores {room_id: set(usernames)}
file_buffer = {}  # Stores {filename: {sender, data_chunks, total_chunks}}

def handle_client(data, client_address):
    global clients, rooms, file_buffer
    
    message = data.decode()
    
    if message.startswith("JOIN:"):
        _, username, room_id = message.split(":")
        clients[username] = (client_address, room_id)

        if room_id not in rooms:
            rooms[room_id] = set()
        rooms[room_id].add(username)

        print(f"{username} joined room {room_id} from {client_address}")

    elif message.startswith("EXIT:"):
        username = message.split(":")[1]
        if username in clients:
            _, room_id = clients[username]
            rooms[room_id].discard(username)
            if not rooms[room_id]:  
                del rooms[room_id]
            del clients[username]
            print(f"{username} left the chat.")

    elif message.startswith("FILE:"):
        _, sender, filename, total_chunks, chunk_index, chunk_data = message.split(":", 5)
        total_chunks, chunk_index = int(total_chunks), int(chunk_index)

        if filename not in file_buffer:
            file_buffer[filename] = {"sender": sender, "data_chunks": {}, "total_chunks": total_chunks}

        file_buffer[filename]["data_chunks"][chunk_index] = chunk_data

        if len(file_buffer[filename]["data_chunks"]) == total_chunks:
            print(f"File {filename} received from {sender}.")
            with open(f"received_{filename}", "wb") as f:
                for i in range(total_chunks):
                    f.write(file_buffer[filename]["data_chunks"][i].encode())
            del file_buffer[filename]

    elif message.startswith("REQUEST_FILE:"):
        _, requester, target_user, filename = message.split(":")
        
        if target_user in clients:
            target_address, _ = clients[target_user]
            server_socket.sendto(f"SEND_FILE:{requester}:{filename}".encode(), target_address)

    else:
        sender_username = message.split(":")[0]
        _, room_id = clients.get(sender_username, (None, None))
        
        if sender_username in clients:
            if message.startswith("@"):
                parts = message.split(" ", 2)
                if len(parts) < 3:
                    return  
                target_user, private_message = parts[1], parts[2]
                
                if target_user in clients:
                    target_address, _ = clients[target_user]
                    server_socket.sendto(f"[Private] {sender_username}: {private_message}".encode(), target_address)
                else:
                    server_socket.sendto("User not found.".encode(), client_address)
            else:
                for user in rooms.get(room_id, set()):
                    if user != sender_username:
                        target_address, _ = clients[user]
                        server_socket.sendto(message.encode(), target_address)

while True:
    data, client_address = server_socket.recvfrom(4096)
    threading.Thread(target=handle_client, args=(data, client_address), daemon=True).start()
