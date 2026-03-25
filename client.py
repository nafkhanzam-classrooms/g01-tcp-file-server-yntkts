import socket
import threading
import os

HOST = '127.0.0.1'
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

base_dir = os.path.dirname(os.path.abspath(__file__))

sedang_download = False
file_download = None
nama_file_download = ""
buffer = b""

def receive():
    global sedang_download, file_download, nama_file_download, buffer

    while True:
        try:
            data = client.recv(1024)
            if not data:
                break

            buffer += data 

            if sedang_download:
                if b"<EOF>" in buffer:
                    content, buffer = buffer.split(b"<EOF>", 1)
                    file_download.write(content)
                    file_download.close()

                    print(f"Download finished: {nama_file_download}")

                    sedang_download = False
                    nama_file_download = ""
                else:
                    file_download.write(buffer)
                    buffer = b""

            else:
                try:
                    text = buffer.decode()

                    if text.startswith("FILE:"):
                        _, filename = text.split(":")

                        nama_file_download = filename.strip()
                        filepath = os.path.join(base_dir, nama_file_download)

                        file_download = open(filepath, "wb")
                        sedang_download = True
                        buffer = b""

                    elif text == "File not found":
                        print(text)
                        buffer = b""

                    else:
                        print(text)
                        buffer = b""

                except:
                    continue

        except:
            print("Connection closed")
            break


threading.Thread(target=receive, daemon=True).start()


while True:
    msg = input()

    if msg.startswith("/upload"):
        _, filename = msg.split()

        filepath = os.path.join(base_dir, filename)

        if not os.path.exists(filepath):
            print("File not found")
            continue

        client.send(msg.encode())

        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(1024)
                if not chunk:
                    break
                client.send(chunk)

        client.send(b"<EOF>")

    elif msg.startswith("/download"):
        client.send(msg.encode())

    elif msg.startswith("/list"):
        client.send(msg.encode())

    else:
        client.send(msg.encode())