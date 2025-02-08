import socket
import threading
import os

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 12345)

nickname = input("Enter your nickname: ")
client_socket.sendto(f"REGISTER:{nickname}".encode(), server_address)

# Function to receive messages & files
def receive_messages():
    file_buffer = {}  # Buffer to store incoming file chunks
    while True:
        try:
            data, _ = client_socket.recvfrom(4096)
            message = data.decode()

            # File Reception Handling
            if message.startswith("FILE:"):
                _, sender, filename, chunk_index, total_chunks, file_data = message.split(":", 5)
                chunk_index, total_chunks = int(chunk_index), int(total_chunks)

                if filename not in file_buffer:
                    file_buffer[filename] = [""] * total_chunks  # Initialize buffer
                
                file_buffer[filename][chunk_index] = file_data

                print(f"Receiving file '{filename}' [{chunk_index + 1}/{total_chunks}] from {sender}")

                # If all chunks are received, save the file
                if None not in file_buffer[filename]:
                    with open(f"received_{filename}", "w") as f:
                        f.write("".join(file_buffer[filename]))
                    print(f"File '{filename}' received successfully!")

            else:
                print(message)

        except Exception as e:
            print("Error receiving message:", e)
            break

# Start receiving thread
receive_thread = threading.Thread(target=receive_messages, daemon=True)
receive_thread.start()

# Function to send files
def send_file(target_nickname, file_path):
    if not os.path.exists(file_path):
        print("File not found!")
        return
    
    with open(file_path, "r") as file:
        data = file.read()

    chunk_size = 1024  # 1 KB per chunk
    chunks = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]

    for i, chunk in enumerate(chunks):
        message = f"FILE:{nickname}:{target_nickname}:{os.path.basename(file_path)}:{i}:{len(chunks)}:{chunk}"
        client_socket.sendto(message.encode(), server_address)

    print(f"File '{file_path}' sent to {target_nickname}!")

# Sending messages
while True:
    message = input()
    
    if message.lower() == "exit":
        client_socket.sendto(f"EXIT:{nickname}".encode(), server_address)
        break
    
    elif message.startswith("@"):  # Unicast message
        client_socket.sendto(f"UNICAST:{nickname}:{message}".encode(), server_address)
    
    elif message.startswith("/sendfile"):  # File sending command: /sendfile @user file.txt
        parts = message.split(" ", 2)
        if len(parts) < 3 or not parts[1].startswith("@"):
            print("Usage: /sendfile @recipient file_path")
        else:
            target = parts[1][1:]  # Remove '@'
            file_path = parts[2]
            send_file(target, file_path)

    elif message.startswith("/requestfile"):  # File request command: /requestfile @user file.txt
        parts = message.split(" ", 2)
        if len(parts) < 3 or not parts[1].startswith("@"):
            print("Usage: /requestfile @recipient filename")
        else:
            target = parts[1][1:]  # Remove '@'
            filename = parts[2]
            client_socket.sendto(f"REQUEST_FILE:{nickname}:{target}:{filename}".encode(), server_address)
    
    else:  # Broadcast message
        client_socket.sendto(f"BROADCAST:{nickname}:{message}".encode(), server_address)

client_socket.close()
print("Exiting from the chat")
