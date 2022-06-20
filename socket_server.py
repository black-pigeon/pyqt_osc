import re
import socket
from collections import deque
import pickle
import struct
import matplotlib.pyplot as plt

class udp_client():
    def __init__(self):
        # Create a udp socket
        self.udp_socket = None
        # Bind udp socket to local 
        self.local_ip = "192.168.1.100"
        self.local_port = 8080
        self.server_is_connected = 0

        # Create a fifo
        self.fifo = deque()
        self.recv_data = b''


    def udp_get_sample(self, addr):
        send_data = [0x55, 0x55, 0x55, 0x55, 0x00, 0x01]
        send_pack = self.getBytesPack(send_data)
        self.udp_socket.sendto(send_pack, addr)
        
        self.recv_data, recv_addr = self.udp_socket.recvfrom(1024)
        ret_data = struct.unpack("1024B", self.recv_data[:1024])
        self.recv_data = self.recv_data[1024:]
        return ret_data

    def getBytesPack(self, array_data):
        bytes_data = bytes()
        for i in range(len(array_data)):
            bytes_data += struct.pack('B', array_data[i])
        return bytes_data  

    
    def connect_to_server(self, address):
        if self.udp_socket == None:
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.udp_socket.connect(address)
        self.udp_socket.bind((self.local_ip, self.local_port))
        print("------conect to server-------")
        self.server_is_connected = 1
    
    def disconnect_from_server(self):
        self.udp_socket.close()
        self.udp_socket = None
        print("------disconnect from server-----------")
        self.server_is_connected = 0
        


if __name__ == "__main__":
    server = udp_client()
    server.connect_to_server(("192.168.1.10", 8080))
    while True:
        ret_data = server.udp_get_sample(("192.168.1.10", 8080))
        print(ret_data)
    
        plt.plot(ret_data)
        plt.show()

