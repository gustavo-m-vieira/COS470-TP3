#imports
import socket
import time
from datetime import datetime
import os
from threading import Thread, Lock

DEBUG = False

mutex = Lock()

HOST = '127.0.0.1'
PORT = 65432

requests = []
clients = {}
inCriticalZone = -1

def changeCriticalZone(id):
  global inCriticalZone
  inCriticalZone = int(id)

def IOThreadHandler():
  while True:
    op=int(input("Digite:\n1 para imprimir fila de pedidos atual.\n2 para imprimir quantas vezes cada processo foi atendido.\n3 para encerrar a execução.\n"))
    if op==1:
      print(requests)
    elif op==2:
      print(clients)
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
  global inCriticalZone
  global mutex
  
  while True:
    data = conn.recv(10)
    if not data:
      break
    
    data = data.decode()

    [op, id, trash] = data.split("|")
    if DEBUG: print(f'Received {op}, {id}')
    
    if (type(clients.get(id)) != int):
      clients[id] = 0
    

    if op == "1":
      requestId = int(datetime.utcnow().strftime('%Y%m%d%H%M%S%f')[:-3])
      
      mutex.acquire()
      requests.append((int(id) , requestId))
      writeLog(op, id)
      mutex.release()
      
      while (inCriticalZone != requestId):
        pass
      
      if DEBUG: print(f"Dentro da area critica {id} {str(inCriticalZone)}")
      
      message = "2|" + id + "|"
      message = message + (10 - len(message))*"0"
      conn.sendall(message.encode())
      writeLog("2", id)
      clients[id] += 1
      
    if op == "3":
      if DEBUG: print('RELEASE')
      writeLog(op, id)
      changeCriticalZone(-1)
      
  conn.close()

def criticalZoneHandler():
  global inCriticalZone
  
  while True:
    if (len(requests) > 0 and inCriticalZone == -1):
      id, requestId = requests.pop(0)
      
      changeCriticalZone(requestId)
      

def writeLog(op, id):
  actualTime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
  if (op == "1"):
    operation = "[R] Request - "
  if (op == "2"):
    operation = "[S] Grant - "
  if (op == "3"):
    operation = "[R] Release - "
  
  message = operation + id + ' - ' +  actualTime + "\n"
  if DEBUG: print(message)
  
  with open("log.txt", "a") as f:
    f.write(message)
  
Thread(target=IOThreadHandler).start()
Thread(target=socketListener).start()
Thread(target=criticalZoneHandler).start()