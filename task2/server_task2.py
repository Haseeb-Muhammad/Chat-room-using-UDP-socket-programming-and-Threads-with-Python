import socket
import threading

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('localhost', 12345))

print("Server is listening on localhost:12345")

clients = {}  # Stores {username: (address, room_id)}
rooms = {}  # Stores {room_id: set(usernames)}

def handle_client(data, client_address):
    global clients, rooms
    
    message = data.decode()
    
    if "joined the chat!" in message:
        # Extract user and room info
        username, _, room_id = message.split(" ", 2)
        clients[username] = (client_address, room_id)
        
        if room_id not in rooms:
            rooms[room_id] = set()
        rooms[room_id].add(username)

        print(f"{username} joined room {room_id} from {client_address}")
    
    elif "left the chat!" in message:
        username = message.split(" ")[0]
        if username in clients:
            _, room_id = clients[username]
            rooms[room_id].discard(username)
            if not rooms[room_id]:  
                del rooms[room_id]
            del clients[username]
            print(f"{username} left the chat.")

    else:
        sender_username = message.split(":")[0]
        _, room_id = clients.get(sender_username, (None, None))
        
        if sender_username in clients:
            if message.startswith("@"):
                # Handle Unicast Message
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
                # Broadcast to the whole room
                for user in rooms.get(room_id, set()):
                    if user != sender_username:
                        target_address, _ = clients[user]
                        server_socket.sendto(message.encode(), target_address)

while True:
    data, client_address = server_socket.recvfrom(4096)
    threading.Thread(target=handle_client, args=(data, client_address), daemon=True).start()
