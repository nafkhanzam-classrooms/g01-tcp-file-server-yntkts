import socket
import select
import os

HOST = '0.0.0.0'
PORT = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

sockets_list = [server_socket]
clients = {}

folder = "server_files"
if not os.path.exists(folder):
    os.makedirs(folder)

print("Server running...")

def broadcast(message, sender_socket):
    for client_socket in clients:
        if client_socket != sender_socket:
            client_socket.send(message.encode())

while True:
    read_sockets, _, _ = select.select(sockets_list, [], [])

    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()
            sockets_list.append(client_socket)
            clients[client_socket] = client_address
            print(f"Client connected: {client_address}")

        else:
            try:
                data = notified_socket.recv(1024).decode()
                if not data:
                    raise Exception()

                if data.startswith("/list"):
                    files = os.listdir(folder)
                    response = "\n".join(files)
                    notified_socket.send(response.encode())

                elif data.startswith("/upload"):
                    _, filename = data.split()
                    path = os.path.join(folder, filename)

                    with open(path, "wb") as f:
                        while True:
                            chunk = notified_socket.recv(1024)
                            if chunk.endswith(b"<EOF>"):
                                f.write(chunk[:-5])
                                break
                            f.write(chunk)

                    notified_socket.send("Upload success\n".encode())

                elif data.startswith("/download"):
                    _, filename = data.split()
                    path = os.path.join(folder, filename)

                    if not os.path.exists(path):
                        notified_socket.send("File not found".encode())
                    else:
                        notified_socket.send(f"FILE:{filename}".encode())

                        with open(path, "rb") as f:
                            while True:
                                chunk = f.read(1024)
                                if not chunk:
                                    break
                                notified_socket.send(chunk)

                        notified_socket.send(b"<EOF>")

                else:
                    broadcast(data, notified_socket)

            except:
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                print("Client disconnect")