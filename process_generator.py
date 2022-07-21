import socket
import time
from datetime import datetime
from threading import Thread

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

def processHandler(id, r, k):
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    
    requestMessage = "1|" + str(id) + "|"
    requestMessage += (10 - len(requestMessage))*"0"
    
    releaseMessage = "3|" + str(id) + "|"
    releaseMessage += (10 - len(releaseMessage))*"0"
    
    for i in range(r):
      s.sendall(requestMessage.encode())
      data = s.recv(10)
      
      data = data.decode()

      [op, idReceived, trash] = data.split("|")
      print(f'Received {op}, my ID: {id} - ID received {idReceived}')
    
      writeFile(id)
      time.sleep(k)
    
      s.sendall(releaseMessage.encode())

def writeFile(id):
  
  actualTime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
  
  message = str(id) + ' - ' +  actualTime + "\n"
  print(message)
  
  with open("resultado.txt", "a") as f:
    f.write(message)

def ProcessGenerator(n,r,k):  
  for i in range(n):
    Thread(target=processHandler, args=(i,r,k)).start()

if __name__ == "__main__":
  n = int(input("Enter n: "))
  r = int(input("Enter r: "))
  k = int(input("Enter k: "))
  ProcessGenerator(n,r,k)