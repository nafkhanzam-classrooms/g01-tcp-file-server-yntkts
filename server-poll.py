import socket
import selectors
import os

HOST = '0.0.0.0'
PORT = 5000
BUFFER_SIZE = 1024
FOLDER = "server_files"

# Pastikan folder ada
if not os.path.exists(FOLDER):
    os.makedirs(FOLDER)

sel = selectors.DefaultSelector()

clients = {}

print("Server running (selectors)...")

# =========================
# Broadcast ke semua client
# =========================
def broadcast(message, sender):
    for client in clients:
        if client != sender:
            try:
                client.send(message.encode())
            except:
                pass

# =========================
# Terima koneksi baru
# =========================
def accept_connection(server_socket):
    client_socket, client_address = server_socket.accept()
    client_socket.setblocking(False)

    sel.register(client_socket, selectors.EVENT_READ, handle_client)
    clients[client_socket] = client_address

    print(f"Client connected: {client_address}")

# =========================
# Handle client
# =========================
def handle_client(client_socket):
    try:
        data = client_socket.recv(BUFFER_SIZE)

        if not data:
            raise Exception()

        text = data.decode(errors="ignore")

        # ======================
        # /list
        # ======================
        if text.startswith("/list"):
            files = os.listdir(FOLDER)
            response = "\n".join(files) if files else "Kosong"
            client_socket.send(response.encode())

        # ======================
        # /upload
        # ======================
        elif text.startswith("/upload"):
            _, filename = text.split()
            path = os.path.join(FOLDER, filename)

            with open(path, "wb") as f:
                while True:
                    chunk = client_socket.recv(BUFFER_SIZE)
                    if chunk.endswith(b"<EOF>"):
                        f.write(chunk[:-5])
                        break
                    f.write(chunk)

            client_socket.send(b"Upload success\n")

        # ======================
        # /download
        # ======================
        elif text.startswith("/download"):
            _, filename = text.split()
            path = os.path.join(FOLDER, filename)

            if not os.path.exists(path):
                client_socket.send(b"File not found")
            else:
                client_socket.send(f"FILE:{filename}".encode())

                with open(path, "rb") as f:
                    while True:
                        chunk = f.read(BUFFER_SIZE)
                        if not chunk:
                            break
                        client_socket.send(chunk)

                client_socket.send(b"<EOF>")

        # ======================
        # CHAT
        # ======================
        else:
            addr = clients[client_socket]
            message = f"[{addr[0]}:{addr[1]}] {text}"
            broadcast(message, client_socket)

    except:
        print(f"Client disconnect: {clients.get(client_socket)}")
        sel.unregister(client_socket)
        client_socket.close()
        if client_socket in clients:
            del clients[client_socket]

# =========================
# MAIN
# =========================
def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    server_socket.setblocking(False)

    sel.register(server_socket, selectors.EVENT_READ, accept_connection)

    while True:
        events = sel.select()

        for key, _ in events:
            callback = key.data
            callback(key.fileobj)

# =========================
if __name__ == "__main__":
    main()