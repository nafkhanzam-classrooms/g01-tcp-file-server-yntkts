import socket
import select
import os
from datetime import datetime

HOST = '0.0.0.0'
PORT = 5000
FOLDER = "server_files"

# Setup folder
if not os.path.exists(FOLDER):
    os.makedirs(FOLDER)

# Setup server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()

sockets_list = [server_socket]
clients = {}

print(f"[{datetime.now().strftime('%H:%M:%S')}] Server running on {HOST}:{PORT}")

def broadcast(message, sender_socket):
    for client_socket in clients:
        if client_socket != sender_socket:
            try:
                client_socket.send(message.encode())
            except:
                pass

def handle_command(data, sock):
    # =====================
    # FORMAT BARU (/command)
    # =====================
    if data.startswith("/list"):
        files = os.listdir(FOLDER)
        response = "\n".join(files) if files else "Kosong"
        sock.send(response.encode())

    elif data.startswith("/upload"):
        _, filename = data.split()
        path = os.path.join(FOLDER, filename)

        with open(path, "wb") as f:
            while True:
                chunk = sock.recv(1024)
                if chunk.endswith(b"<EOF>"):
                    f.write(chunk[:-5])
                    break
                f.write(chunk)

        sock.send("Upload success\n".encode())

    elif data.startswith("/download"):
        _, filename = data.split()
        path = os.path.join(FOLDER, filename)

        if not os.path.exists(path):
            sock.send("File not found".encode())
        else:
            sock.send(f"FILE:{filename}".encode())

            with open(path, "rb") as f:
                while True:
                    chunk = f.read(1024)
                    if not chunk:
                        break
                    sock.send(chunk)

            sock.send(b"<EOF>")

    # =====================
    # FORMAT LAMA (PROTO : )
    # =====================
    elif ":" in data:
        bagian = data.split(":", 2)
        perintah = bagian[0]

        if perintah == "LIST":
            files = os.listdir(FOLDER)
            hasil = "FILE_LIST:" + (",".join(files) if files else "Kosong")
            sock.send(hasil.encode())

        elif perintah == "UPLOAD":
            nama, isi = bagian[1], bagian[2]
            path = os.path.join(FOLDER, nama)

            with open(path, "w") as f:
                f.write(isi)

            sock.send(f"SUCCESS:Upload {nama} berhasil".encode())

        elif perintah == "DOWNLOAD":
            nama = bagian[1]
            path = os.path.join(FOLDER, nama)

            if os.path.exists(path):
                with open(path, "r") as f:
                    isi = f.read()
                sock.send(f"FILE_DATA:{nama}:{isi}".encode())
            else:
                sock.send(f"ERROR:File {nama} tidak ada".encode())

        elif perintah == "CHAT":
            teks = bagian[1]
            broadcast(f"[CHAT] {teks}", sock)

        else:
            sock.send("ERROR:Perintah tidak dikenali".encode())

    # =====================
    # DEFAULT → CHAT BROADCAST
    # =====================
    else:
        broadcast(data, sock)


# =====================
# MAIN LOOP (MULTI CLIENT)
# =====================
while True:
    read_sockets, _, _ = select.select(sockets_list, [], [])

    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()
            sockets_list.append(client_socket)
            clients[client_socket] = client_address
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Connected: {client_address}")

        else:
            try:
                data = notified_socket.recv(4096).decode()

                if not data:
                    raise Exception()

                handle_command(data, notified_socket)

            except:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Client disconnected")
                sockets_list.remove(notified_socket)
                del clients[notified_socket]