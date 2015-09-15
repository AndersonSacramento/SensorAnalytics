#!/usr/bin/env python
import web
import shelve
import socket
import xml.etree.ElementTree as ET
from BroadcastingUrl import BroadcastingUrl
import json
from StringIO import StringIO

render = web.template.render("")
BUFFER_SIZE = 1024  # Normally 1024, but we want fast response
#tree = ET.parse('user_data.xml')
#root = tree.getroot()

urls = (
    '/taskAgenda', 'task_agenda',
    '/taskResults','task_result',
    '/dev', 'device_config',
    '/taskAgendaDevice/(.*)', 'task_agenda_device'

)

app = web.application(urls, globals())

# class device_connection:
#     def __init__(self,ip,port,duration):
#         self.ip = ip
#         self.port = int(port)
#         self.duration = int(duration)
        
#     def startConnection(self):
#         import socket
#         self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.connection.connect((self.ip, self.port))
#         self.chat()

#     def chat(self):
#         import json
#         from StringIO import StringIO
#         io = StringIO()
#         json.dump({'task-duration':self.duration}, io)
#         self.connection.send(io.getvalue())
#         while 1:
#             data = self.connection.recv(BUFFER_SIZE)
#             if not data: break
#             print "receiving data:", data
#         self.connection.close()

class device_config:
    def GET(self):
        web.header('Content-Type', 'application/json')
        web.header('Access-Control-Allow-Origin', '*')
        devices =  self.get_devices()
        print devices
        return json.dumps(    devices    )

    def POST(self):
        data = web.input()
        ip_device = data.device_ip
        device_name = data.device_name
        print ip_device, device_name
        self.save_device(ip_device, device_name)
        
    def save_device(self, ip_device,device_name):
        s = shelve.open('shelve_devices.db', flag='c', writeback = True)
        try:
            s[str(device_name)] = ip_device
            devices = s.keys()
            print 'Devices\n'
            for d in devices:
                print d,'\n'
        finally:
            s.close()

    def get_devices(self):
        s = shelve.open('shelve_devices.db', flag = 'c')
        try:
            devices = s.keys()
        finally:
            s.close()
        return devices

class task_result:
    #Obtem resultados browser -> webservice
    def GET(self,id, device_name):
        result = tasks[codigo]
        return result
    
    #Fornece dados device -> webservice    
    def POST(self,codigo):
        data = web.input()
        ip = data.device_ip
        sensor_data = data.sensor_data
        
class task_agenda_device:
    def GET(self, device_name):
        task  = self.get_first_undone_task(device_name) #exemplo de dados de uma tarefa
        if not task: return None
        io  = StringIO()
        json.dump(task,io)
        output = io.getvalue()
        return output

    def get_first_undone_task(self, device_name):
        s = shelve.open('shelve_devices_agenda.db', flag = 'c')
        try:
            device = str(device_name)
            if not s.has_key(device): raise KeyError
            agenda = s[device]['agenda'] 
            tasks =  agenda.keys()
            for t in tasks:
                if t['done'] == False:
                    id_last_undone = t.key()
                    break
            else:
                s.close()
                return {'id':id_last_undone, 'duration':t['duration'], 'frequency':t[frequency],'done':t['done']}
        except KeyError:
            print 'Do not has key.'
        finally:
            print 'close shelve'
            s.close()
        return None

class task_agenda:        
    def POST(self):
        data = web.input() # you can get data use this method
        device_name =  data.device_name
        duration = data.duration_seconds
        frequency = data.frequency_milliseconds
        self.save_agenda(device_name, duration, frequency)
        #dev = DeviceConnection(ip,port,duration)
        #dev.startConnection()

    def save_agenda(self, device_name, duration, frequency):
        s = shelve.open('shelve_devices_agenda.db', flag = 'c',writeback = True)
        try:
            device = str(device_name)
            if not s.has_key(device):
                id = 1
            else:
                last = s[device]['agenda'].last()
                id = int(last.key())
            print 'New id:',id
            s[device]['agenda'][id]['duration'] = duration
            s[device]['agenda'][id]['frequency'] = frequency
            s[device]['agenda'][id]['done'] = False
        finally:
            s.close()

        
if __name__ == "__main__":
    url_sender = BroadcastingUrl()
    url_sender.start()
    app.run()
    
