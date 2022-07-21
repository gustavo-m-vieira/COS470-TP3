def getGrant():
  grants = []
  
  with open("log.txt", "r") as f:
    lines = f.readlines()
    for line in lines:
      if ("[S] Grant" in line):
        grants.append(int(line.split("-")[1]))
  return grants

def getResultadoIds():
  resultadoIds = []
  
  with open("resultado.txt", "r") as f:
    lines = f.readlines()
    for line in lines:
      resultadoIds.append(int(line.split("-")[0]))
  return resultadoIds

grants = getGrant()
resultadoIds = getResultadoIds()

for i in range(len(grants)):
  if (grants[i] != resultadoIds[i]):
    raise Exception("Invalid log file: invalid grants and resultadoIds sequence")

print("Resultado file was successfully validated")