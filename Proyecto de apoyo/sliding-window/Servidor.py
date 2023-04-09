import socket               # Módulo del Socket
from time import sleep
from random import random
s = socket.socket()         # Crea un objeto del socket
host = socket.gethostname()  # Otener el nombre de la máquina
port = 8080                # Guardar el puerto del servicio
s.bind((host, port))        # Vincula el puerto
s.listen(5)                 # Espera la conexión del cliente

data = [None] * 1024
rl, rw = 0, 4
c, addr = s.accept()
print('Conexión de ', addr)
while True:
    try:
        i, d = c.recv(4096).split(",")
        i = int(i)
        print("Frame recibido ", i, " Data : ", d)
        if i < rl + rw:
            data[i] = d
            if random() < 0.8 :        #Tasa de transmisión de un 80%
                c.send(str(i) + ',')
                if(i == rl):
                    while data[rl] is not None:
                        rl += 1         #Incrementa el RL
                        print("RL se incrementa a ", rl)
            else:
                print("ACK ", i, " No enviado")
        else:
            print("Descartado ", i)
        sleep(0.5)

    except Exception as e:
        c.close()
        break

print("Data Recibida : ", )
for d in data:
    if d is None:
        break
    print(d, )
