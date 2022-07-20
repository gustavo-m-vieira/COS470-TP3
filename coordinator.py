#imports
import socket
import time
import os
import numpy as np 
from threading import Thread

HOST = '127.0.0.1'
PORT = 65432

requests = []
clients = {}
inCriticalZone = -1


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
  while True:
    data = conn.recv(10)
    if not data:
      break

    op, id = data.decode().split("|")
    
    if (type(clients[id]) != int):
      clients[id] = 0
    

    if op == "1":
      requests.append(int(id))
      writeLog(op, id)
      
      while (inCriticalZone != int(id)):
        pass
      
      message = "2|" + id + "|"
      conn.sendAll(message + (10 - len(message))*"0")
      writeLog("2", id)
      clients[id] += 1
      
    if op == "3":
      inCriticalZone = -1
      writeLog(op, id)
  conn.close()

def criticalZoneHandler():
  while True:
    if (len(requests) > 0 and inCriticalZone == -1):
      inCriticalZone = requests[0]
      requests.pop(0)

def writeLog(op, id):
  actualTime = time.strftime('%H:%M:%S, ', time.localtime())
  if (op == "1"):
    operation = "[R] Request - "
  if (op == "2"):
    operation = "[S] Grant - "
  if (op == "3"):
    operation = "[R] Release - "
  
  message = operation + id + ' - ' +  actualTime + "\n"
  print(message)
  
  with open("log.txt", "a") as f:
    f.write(message)
  
Thread(target=IOThreadHandler).start()
Thread(target=socketListener).start()
Thread(target=criticalZoneHandler).start()