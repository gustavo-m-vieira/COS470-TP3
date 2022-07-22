#imports
import socket
import time
from datetime import datetime
import os
from threading import Thread, Lock

DEBUG = False

requestLock = Lock()
criticalZoneLock = Lock()
clientsLock = Lock()

HOST = '127.0.0.1'
PORT = 65432

requests = []
clients = {}

def IOThreadHandler():
  global requestLock
  global clientsLock
  
  while True:
    op=int(input("Digite:\n1 para imprimir fila de pedidos atual.\n2 para imprimir quantas vezes cada processo foi atendido.\n3 para encerrar a execução.\n"))
    if op==1:
      requestLock.acquire()
      print([id for id, requestId, conn in requests])
      requestLock.release()
      
    elif op==2:
      clientsLock.acquire()
      print(clients)
      clientsLock.release()
    elif op==3:
      os.abort()

def socketListener():
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    while True:
      conn, addr = s.accept()
      Thread(target=clientSocketHandler, args=(conn,addr)).start()

def clientSocketHandler(conn, addr):
  global criticalZoneLock
  global requestLock
  
  while True:
    data = conn.recv(10)
    if not data:
      break
    
    data = data.decode()

    [op, id, trash] = data.split("|")
    if DEBUG: print(f'Received {op}, {id}')
    
    
    
    if op == "1":
      requestId = int(datetime.utcnow().strftime('%Y%m%d%H%M%S%f')[:-3])
      
      requestLock.acquire()
      requests.append((int(id) , requestId, conn))
      writeLog(op, id)
      requestLock.release()

    if op == "3":
      if DEBUG: print('RELEASE')
      writeLog(op, id)
      criticalZoneLock.release()
      
  conn.close()

def criticalZoneHandler():
  global criticalZoneLock
  global clientsLock
  global requestLock

  
  while True:
    if (len(requests) > 0):
      criticalZoneLock.acquire()

      requestLock.acquire()
      id, requestId, conn = requests.pop(0)
      requestLock.release()
      
      if DEBUG: print(f"Dentro da area critica {id} - requestId {requestId}")
      
      message = "2|" + str(id) + "|"
      message = message + (10 - len(message))*"0"
      if DEBUG: print(message)
      
      conn.sendall(message.encode())
      writeLog("2", id)
      
      clientsLock.acquire()
      if (type(clients.get(id)) != int):
        clients[id] = 0

      clients[id] += 1
      clientsLock.release()
      

def writeLog(op, id):
  actualTime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
  if (op == "1"):
    operation = "[R] Request - "
  if (op == "2"):
    operation = "[S] Grant - "
  if (op == "3"):
    operation = "[R] Release - "
  
  message = operation + str(id) + ' - ' +  actualTime + "\n"
  if DEBUG: print(message)
  
  with open("log.txt", "a") as f:
    f.write(message)
  
def Coordinator():
  print(f"My PID: {os.getpid()}")
  
  Thread(target=IOThreadHandler).start()
  Thread(target=socketListener).start()
  Thread(target=criticalZoneHandler).start()

if __name__ == "__main__":
  Coordinator()