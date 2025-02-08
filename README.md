# P2P Chat and File Transfer Application  

A simple peer-to-peer chat application with file sharing capabilities, built using Python and UDP sockets. The application allows users to send messages, share files, and request files from other users in the chat.  

## Features  
- **User Registration**: Users can register with a unique nickname.  
- **Unicast Messaging**: Send private messages to a specific user using `@<nickname> <message>`.  
- **Broadcast Messaging**: Send messages to all connected users.  
- **File Transfer**: Share files with other users using the `/sendfile` command.  
- **File Request**: Request a file from another user using the `/requestfile` command.  
- **Exit Chat**: Gracefully leave the chat using the `exit` command.  

## Prerequisites  
- Python 3.x  
- Basic understanding of networking and sockets.  

## How to Run  
1. **Start the Server**:  
   - Run the server script:  
     ```bash  
     python server.py  
     ```  
   - The server will start listening on `localhost:12345`.  

2. **Start the Client**:  
   - Run the client script:  
     ```bash  
     python client.py  
     ```  
   - Enter a unique nickname when prompted.  

3. **Chat and Share Files**:  
   - Send messages:  
     - Broadcast: `Hello everyone!`  
     - Unicast: `@alice Hi Alice!`  
   - Share files: `/sendfile @alice file.txt`  
   - Request files: `/requestfile @bob file.txt`  
   - Exit the chat: `exit`  

## Code Structure  
- **`client.py`**: Handles the client-side logic, including sending/receiving messages and files.  
- **`server.py`**: Manages the server-side logic, including client registration and message/file routing.  

## How File Transfer Works  
- Files are split into chunks of 1KB and sent over the network.  
- The server forwards each chunk to the intended recipient.  
- The recipient reassembles the file once all chunks are received.  

## Future Improvements  
- Add encryption for secure communication.  
- Implement error handling for file transfers.  
- Support for larger files and progress tracking.  
- Add a GUI for better user experience.  

## Contributing  
Feel free to contribute to the project by opening issues or submitting pull requests.  
