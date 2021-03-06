# Send UDP broadcast packets
import sys, time,thread,os
import socket 
import netifaces as ni
import fcntl
import struct

PORT = 2015

class BroadcastingUrl:
    
    def start(self):
        thread.start_new_thread( self.send_msg,())

   
    def send_msg(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.bind(('', PORT))
        
        self.get_lan_ip()
        self.ip = str("url:"+self.ip)
        print self.ip
        while 1:
           # data = repr(time.time()) + '\n'
            s.sendto(self.ip, ('<broadcast>',PORT))
            time.sleep(2)


    def get_lan_ip(self):
        self.ip = socket.gethostbyname(socket.gethostname())
        if (self.ip.startswith("127.") or self.ip.startswith("0.")):
            interfaces = ["eth0","eth1","Eth2","wlan0","wlan1","wifi0","ath0","ath1","ppp0"]
            for ifname in interfaces:
                try:
                    self.ip = self.get_interface_ip("eth1")
                    break;
                except IOError:
                    pass
      

    def get_interface_ip(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', (ifname[:15])))[20:24])

