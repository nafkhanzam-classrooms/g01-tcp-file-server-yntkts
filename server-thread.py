import socket
import threading
import os

HOST = '0.0.0.0'
PORT = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

clients = []

folder = "server_files"
if not os.path.exists(folder):
    os.makedirs(folder)

print("Server running...")

def broadcast(message, sender_conn):
    for client in clients:
        if client != sender_conn:
            try:
                client.send(message.encode())
            except:
                pass

def handle_client(conn, addr):
    print(f"Client connected: {addr}")
    clients.append(conn)

    try:
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break

            if data.startswith("/list"):
                files = os.listdir(folder)
                response = "\n".join(files)
                conn.send(response.encode())

            elif data.startswith("/upload"):
                _, filename = data.split()
                path = os.path.join(folder, filename)

                with open(path, "wb") as f:
                    while True:
                        chunk = conn.recv(1024)
                        if chunk.endswith(b"<EOF>"):
                            f.write(chunk[:-5])
                            break
                        f.write(chunk)

                conn.send("Upload success".encode())

            elif data.startswith("/download"):
                _, filename = data.split()
                path = os.path.join(folder, filename)

                if not os.path.exists(path):
                    conn.send("File not found".encode())
                else:
                    conn.send(f"FILE:{filename}".encode())

                    with open(path, "rb") as f:
                        while True:
                            chunk = f.read(1024)
                            if not chunk:
                                break
                            conn.send(chunk)

                    conn.send(b"<EOF>")

            else:
                broadcast(data, conn)

    except:
        pass

    print(f"Client disconnect: {addr}")
    clients.remove(conn)
    conn.close()

while True:
    conn, addr = server_socket.accept()
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()