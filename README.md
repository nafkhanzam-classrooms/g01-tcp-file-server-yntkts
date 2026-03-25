[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/mRmkZGKe)
# Network Programming - Assignment G01

## Anggota Kelompok
| Nama           | NRP        | Kelas     |
| ---            | ---        | ----------|
| Pradhipta Raja Mahendra               |  5025241055          |      D     |
| Andie Azril Alfrianto               |  5025241054          |     D      |

## Link Youtube (Unlisted)
Link ditaruh di bawah ini
```

```

## Penjelasan Program

### ```server-sync.py```

1. Inisialisasi & Konfigurasi Awal <br>
   Server dikonfigurasi untuk mendengarkan di semua interface (0.0.0.0) pada port 5000. Saat pertama kali dijalankan, server membuat folder server_files jika belum ada — folder ini digunakan sebagai tempat penyimpanan file yang diunggah klien. Socket server dibuat dengan protokol TCP (SOCK_STREAM), lalu di-bind dan mulai mendengarkan koneksi masuk.
Dua struktur data penting diinisialisasi di sini:

    - sockets_list — daftar semua socket aktif (termasuk server socket itu sendiri)
    - clients — dictionary yang memetakan setiap socket klien ke alamat IP-nya


2. Fungsi broadcast() <br>
Fungsi ini bertugas mengirim pesan ke semua klien kecuali pengirimnya sendiri. Ini adalah inti dari fitur chat — ketika satu klien mengirim pesan, semua klien lain akan menerimanya. Pengiriman dibungkus dalam blok try/except agar satu klien yang bermasalah tidak menghentikan broadcast ke klien lainnya.

3. Fungsi handle_command() — Pemrosesan Perintah <br>
Ini adalah fungsi utama yang memproses setiap data yang diterima dari klien.

     - /list — mengembalikan daftar file yang ada di folder server
     - /upload <filename> — menerima file dari klien secara binary dalam bentuk chunk 1024 byte, dengan penanda akhir <EOF>
     - /download <filename> — mengirim file ke klien secara binary, diawali header FILE:<nama> dan diakhiri <EOF>

4. Main Loop — Multiplexing dengan select() <br>
Jantung dari server ini adalah loop tak terbatas yang menggunakan select.select() untuk memantau semua socket secara efisien tanpa blocking. Cara kerjanya:

     - select() mengembalikan daftar socket yang siap dibaca (ada data masuk)
     - Jika socket yang aktif adalah server_socket, berarti ada klien baru yang ingin terhubung — server menerimanya dan mendaftarkannya ke sockets_list dan clients
     - Jika socket lainnya yang aktif, berarti klien yang sudah terhubung mengirim data — server membacanya dan meneruskan ke handle_command()
     - Jika data kosong atau terjadi error (klien disconnect), socket tersebut dihapus dari kedua daftar secara bersih


<br>
<br>

### ```server-poll.py```
1. Konfigurasi Awal <br>

     - HOST = '0.0.0.0' — server mendengarkan dari semua interface jaringan yang tersedia.
     - PORT = 5000 — port yang digunakan untuk koneksi masuk.
     - BUFFER_SIZE = 1024 — ukuran potongan data (chunk) yang dibaca setiap kali, sebesar 1024 byte.
     - FOLDER = "server_files" — direktori tempat file yang diupload disimpan. Jika folder belum ada, os.makedirs() akan membuatnya secara otomatis.
     - sel = selectors.DefaultSelector() — objek selector untuk memantau banyak socket secara bersamaan (non-blocking).
     - clients = {} — dictionary untuk menyimpan pemetaan antara socket client dan alamat IP:port-nya.


2. Fungsi broadcast(message, sender) <br>
Mengirim pesan chat ke semua client yang terhubung, kecuali pengirimnya sendiri. Iterasi dilakukan pada semua socket di clients, dan pesan di-encode ke bytes sebelum dikirim. Jika pengiriman ke salah satu client gagal, error diabaikan dengan pass agar server tetap berjalan.

3. Fungsi accept_connection(server_socket) <br>
Dipanggil otomatis saat ada client baru yang mencoba terhubung. Server menerima koneksi dengan server_socket.accept(), lalu mengatur socket client menjadi non-blocking (setblocking(False)). Socket tersebut kemudian didaftarkan ke selector agar dipantau untuk event baca, dengan handle_client sebagai callback-nya. Alamat client disimpan ke dictionary clients.

4. Fungsi handle_client(client_socket) — Inti Server***
Fungsi ini menangani semua perintah yang dikirim client. Data diterima dengan recv(BUFFER_SIZE) lalu di-decode. Terdapat empat cabang logika:

    - /list — Menampilkan daftar file yang ada di folder server_files. Jika kosong, kirim respons "Kosong".
    - /upload <filename> — Menerima file dari client secara bertahap (chunk by chunk). Server terus membaca data hingga menemukan penanda <EOF> di akhir chunk, yang menandai akhir pengiriman file. File disimpan ke server_files/.
    - /download <filename> — Mengirim file ke client. Server pertama mengirim header FILE:<filename>, lalu membaca file dalam potongan-potongan dan mengirimkannya. Setelah selesai, penanda <EOF> dikirim sebagai sinyal akhir data.
    - Pesan biasa (chat) — Jika input tidak diawali perintah apapun, dianggap sebagai pesan chat. Pesan diformat menjadi [IP:PORT] pesan lalu di-broadcast ke semua client lain.


5. Fungsi main() — Event Loop
Membuat server socket TCP (AF_INET, SOCK_STREAM), melakukan bind ke HOST:PORT, dan mulai listen. Socket server juga diatur non-blocking dan didaftarkan ke selector. Program kemudian masuk ke infinite loop yang terus memanggil sel.select() — metode ini memblokir hingga ada socket yang siap dibaca, lalu menjalankan callback yang sesuai (accept_connection atau handle_client) untuk setiap event yang terjadi.
<br>

### ```server-select.py```

Inisialisasi & Konfigurasi Awal
Server dikonfigurasi untuk mendengarkan di semua interface (0.0.0.0) pada port 5000. Saat dijalankan, server membuat folder server_files jika belum ada. Socket dibuat menggunakan TCP, lalu di-bind dan mulai listen. Dua struktur data utama:

`sockets_list` — daftar semua socket aktif
`clients` — mapping socket klien ke alamatnya
Fungsi `broadcast()`
Mengirim pesan ke semua klien kecuali pengirim. Digunakan untuk fitur chat, dengan try/except agar error pada satu klien tidak mengganggu yang lain.

Pemrosesan Perintah
Server menangani beberapa perintah dari klien:
/list — menampilkan daftar file
/upload — menerima file per chunk hingga <EOF>
/download — mengirim file diawali FILE: dan diakhiri <EOF>
Main Loop — Multiplexing dengan select()

Server menggunakan select.select() untuk memantau semua socket tanpa blocking:
1. Jika server_socket aktif → ada klien baru, lalu ditambahkan ke daftar
2. Jika socket klien aktif → data dibaca dan diproses
3. Jika klien disconnect → socket dihapus dari daftar
<br>

### ```server-thread.py```

Inisialisasi & Konfigurasi Awal
Server berjalan di 0.0.0.0:5000, membuat folder server_files, dan menggunakan socket TCP. Tidak menggunakan select, tetapi list clients untuk menyimpan koneksi aktif.

Fungsi `broadcast()`
Mengirim pesan ke semua klien lain. Error ditangani agar tidak mengganggu koneksi lain.

Fungsi `handle_client()`
Setiap klien ditangani dalam fungsi ini:
/list — menampilkan file
/upload — menerima file hingga <EOF>
/download — mengirim file dengan format FILE:
selain itu — broadcast sebagai chat
Jika terjadi error atau disconnect, klien dihapus dari daftar.

Main Loop — Multithreading
Server menerima koneksi dengan accept(), lalu membuat thread baru untuk setiap klien menggunakan threading.Thread. Dengan ini, banyak klien bisa dilayani secara bersamaan.

### `client.py`

Inisialisasi & Koneksi
Client dibuat dengan socket TCP dan terhubung ke server menggunakan connect(). Menentukan base_dir untuk membaca file upload dan menyimpan file download.

Thread receive()
Client menjalankan thread untuk menerima data dari server. Data disimpan dalam buffer untuk menangani data yang terpotong. Jika menerima FILE:, client masuk mode download dan menyimpan file hingga <EOF>. Jika bukan, ditampilkan sebagai pesan biasa.

Loop Input
Client membaca input user dan mengirim ke server:
/upload — kirim file per chunk + <EOF>
/download — minta file
/list — minta daftar file
selain itu — kirim sebagai chat

## Screenshot Hasil
<img width="529" height="85" alt="image" src="https://github.com/user-attachments/assets/ce60836c-e4ae-4c50-be16-5de7cda97e0b" />
<br>
<img width="578" height="310" alt="image" src="https://github.com/user-attachments/assets/8478754a-c4b9-4b01-8452-00c8d2eab8a3" />
<br>
<img width="554" height="75" alt="image" src="https://github.com/user-attachments/assets/e2933f31-95b9-4a4e-b07e-3d15acb479a0" />


