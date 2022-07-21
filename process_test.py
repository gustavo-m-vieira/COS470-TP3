import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
  s.connect((HOST, PORT))
  s.sendall("1|2|000000".encode())
  data = s.recv(10)

  print(f"Received {data!r}")
  
  s.sendall("3|2|000000".encode())