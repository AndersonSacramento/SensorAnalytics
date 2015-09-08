 #!/usr/bin/env python
import socket, json

TCP_IP = '127.0.0.1'
TCP_PORT = 5005
BUFFER_SIZE = 1024  # Normally 1024, but we want fast response

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
 
conn, addr = s.accept()
print 'Connection address:', addr
data = conn.recv(BUFFER_SIZE)
obj = json.JSONDecoder().decode(str(data))
duration = int(obj['task-duration'])
print duration
f = open('dados.jsonp','r')
if not f: coon.close()

while 1:
   data = f.read(BUFFER_SIZE)
   if not data: break
   print "sending data:", data
   conn.send(data)  # echo
conn.close()
