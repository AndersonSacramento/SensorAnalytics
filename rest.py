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
    def GET(self):
        data = web.input()
        device_name = data.device_name
        id_task = data.id_task
        client_name = data.client_name
        result = get_task_result(client_name, device_name, codigo_task)
        return result
    
    #Fornece dados device -> webservice    
    def POST(self):
        data = web.input()
        device_name = data.device_name
        id_task = data.id_task
        client_name = data.client_name
        result = data.result
        save_result(client_name,device_name,id_task,result)

    def get_task_result(client_name, device_name, codigo_task):
        client_name = str(client_name)
        device_name = str(device_name)
        codigo_task = int(codigo_task)

        s = shelve.open('shelve_devices_agenda.db', flag = 'c',writeback = True)
        try:
            if not s.has_key(device_name):
                s.close()
                return False
            if not s[device_name]:
                s.close()
                return False
            if s[device_name][client_name][id_task]['done']:
                s.close()
                return s[device_name][client_name][id_task]['result']
            else:
                s.close()
                return None
        finally:
            s.close()


    def save_result(self, client_name, device_name, id_task, result):
        client_name = str(client_name)
        device_name = str(device_name)
        id_task = int(id_task)
        s = shelve.open('shelve_devices_agenda.db', flag = 'c',writeback = True)
        try:
            if not s.has_key(device_name):
                s.close()
                return False
            if not s[device_name]:
                s.close()
                return False
            s[device_name][client_name][id_task]['result'] = result
            s[device_name][client_name][id_task]['done'] = True
        finally:
            s.close()

class task_agenda_device:
    def GET(self, device_name):
        task  = self.get_first_undone_task(device_name) #exemplo de dados de uma tarefa
        if not task: return []
        io  = StringIO()
        json.dump(task,io)
        output = io.getvalue()
        return output

    def get_first_undone_task(self, device_name):
        device_name = str(device_name)
        s = shelve.open('shelve_devices_agenda.db', flag = 'c')
        try:
            if not s.has_key(device_name): raise KeyError
            agenda_clients = s[device_name].values()
            for client in agenda_clients:
                for task in client:
                    if task['done'] == False:
                        s.close()
                        task['device_name'] = device_name
                        return task 
        except KeyError:
            print 'Do not has key.'
        finally:
            print 'close shelve'
            s.close()
        return None
    
class task_agenda:
    def GET(self):
        web.header('Content-Type', 'application/json')
        web.header('Access-Control-Allow-Origin', '*')
        data = web.input()
        client_name = data.client_name
        device_name = data.device_name
        return self.get_tasks_in_agenda(client_name, device_name)
    
    def POST(self):
        data = web.input() # you can get data use this method
        client_name = data.client_name
        device_name =  data.device_name
        duration = data.duration_seconds
        frequency = data.frequency_milliseconds
        self.save_agenda(client_name,device_name, duration, frequency)
        #dev = DeviceConnection(ip,port,duration)
        #dev.startConnection()

    def get_tasks_in_agenda(self,client_name, device_name):
        client_name = str(client_name)
        device_name = str(device_name)
        print(client_name,device_name)
        s = shelve.open('shelve_devices_agenda.db', flag = 'c',writeback = True)
        try:
            if not s.has_key(device_name):
                s.close()
                return []
            ids =  []
            for task in s[device_name][client_name]:
                ids.append(task['id'])
                print(task, task['id'])
            print(ids)
        finally:
            s.close()
        return ids

    def save_agenda(self, client_name, device_name, duration, frequency):
        client_name = str(client_name)
        device_name = str(device_name)
        duration = int(duration)
        frequency = int(frequency)
        s = shelve.open('shelve_devices_agenda.db', flag = 'c',writeback = True)
        try:
            if not s.has_key(device_name):
                s[device_name] = {}

            if not s[device_name].has_key(client_name):
                s[device_name][client_name] = []
            id_task = len(s[device_name][client_name])
            print 'New id:',id_task
            s[device_name][client_name].append({
                'id':id_task,
                'duration':duration,
                'frequency':frequency,
                'done':False
            })
        finally:
            s.close()

        
if __name__ == "__main__":
    url_sender = BroadcastingUrl()
    url_sender.start()
    app.run()
    
