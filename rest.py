#!/usr/bin/env python
import web
import xml.etree.ElementTree as ET

BUFFER_SIZE = 1024  # Normally 1024, but we want fast response
#tree = ET.parse('user_data.xml')
#root = tree.getroot()

urls = (
    '/taskAgenda', 'task_agenda'
    '/taskResults','task_result'
    '/dev/(.*)', 'DeviceConfig'

)

app = web.application(urls, globals())

class device_connection:
    def __init__(self,ip,port,duration):
        self.ip = ip
        self.port = int(port)
        self.duration = int(duration)
        
    def startConnection(self):
        import socket
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((self.ip, self.port))
        self.chat()

    def chat(self):
        import json
        from StringIO import StringIO
        io = StringIO()
        json.dump({'task-duration':self.duration}, io)
        self.connection.send(io.getvalue())
        while 1:
            data = self.connection.recv(BUFFER_SIZE)
            if not data: break
            print "receiving data:", data
        self.connection.close()

class device_config:
    def GET(self,device_ip):
        

class task_result:
    #Obtem resultados browser -> webservice
    def GET(self,codigo):
        result = tasks[codigo]
        return result
    
    #Fornece dados device -> webservice    
    def POST(self,codigo):
        data = web.input()
        ip = data.device_ip
        sensor_data = data.sensor_data

class task_agenda:        
    def GET(self,device_ip):
        task  = { 'freq':2, 'duration':1, 'codigo':110} #exemplo de dados de uma tarefa
        return json.dump(task)

    def POST(self):
        data = web.input() # you can get data use this method
        ip =  data.device_ip
        port =  data.device_port
        duration = data.duration_minutes
        print ip, port, duration
        dev = DeviceConnection(ip,port,duration)
        dev.startConnection()
        
if __name__ == "__main__":
    app.run()
