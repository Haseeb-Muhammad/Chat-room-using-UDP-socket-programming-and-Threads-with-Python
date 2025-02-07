import socket
import threading

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 12345)

nickname = input("Enter your nickname: ")
client_socket.sendto(f"REGISTER:{nickname}".encode(), server_address)

# Function to continuously receive messages
def receive_messages():
    while True:
        try:
            data, _ = client_socket.recvfrom(4096)
            print(f"{data.decode()}")
        except:
            break

# Start the receiving thread
receive_thread = threading.Thread(target=receive_messages, daemon=True)
receive_thread.start()

# Sending messages
while True:
    message = input()
    
    if message.lower() == "exit":
        client_socket.sendto(f"EXIT:{nickname}".encode(), server_address)
        break
    
    elif message.startswith("@"):  # Unicast message format: @nickname message
        client_socket.sendto(f"UNICAST:{nickname}:{message}".encode(), server_address)
    
    else:  # Broadcast message
        client_socket.sendto(f"BROADCAST:{nickname}:{message}".encode(), server_address)

client_socket.close()
print("Exiting from the chat")
