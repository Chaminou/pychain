
import time
import socket
import pickle
import threading
from sdy_lib import *

def get_sold(ip, port, socket) :
    miner.available_utxo()
    pickled_address = socket.recv(1048576)
    address = pickle.loads(pickled_address)
    with lock :
        list_of_wallet_utxo = miner.get_utxo_by_address(address)
    pickled_list_of_wallet_utxo = pickle.dumps(list_of_wallet_utxo)
    socket.send(pickled_list_of_wallet_utxo)

def send_sdy(ip, port, socket) :
    miner.available_utxo()
    pickled_transaction = socket.recv(1048576)
    transaction = pickle.loads(pickled_transaction)
    with lock :
        miner.temp_transaction.append(transaction)
        miner.verify_temp_transaction_list()

    print(miner.block.transaction)



class ClientThread(threading.Thread):

    def __init__(self, ip, port, socket):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.socket = socket
        print("[+] New thread started for " + ip + ":"+ str(port))

    def run(self):
        print("Connection from : " + ip + ":" + str(port))

        data = "dummydata"

        while True:
            if not data :
                break
            data = self.socket.recv(1024)
            command = data.decode('utf-8')

            if command == 'get_sold' :
                get_sold(self.ip, self.port, self.socket)
            elif command == 'send_sdy' :
                send_sdy(self.ip, self.port, self.socket)
            else :
                print(command + ' unknown command')

        self.socket.close()
        print("Client disconnected...")
        print(list_of_message)

if __name__ == "__main__" :


    lock = threading.Lock()

    host = '172.18.110.11'
    port = 4747

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))

    threads = []

    block = Block()
    miner =  Miner(block)
    first_transaction = Transaction([('None', None)], [('19HB4ECfCoGsiwzDWpGDVEwBpkg83b2q5v', 100), ('14LRGBn94deQNE4eEG8F2ve7rmyoEATKw4', 100)], 'None')
    block.add_transaction(first_transaction)
    miner.available_utxo()

    while True :
        s.listen(4)
        print("Listening for incoming connections...")
        (clientsock, (ip, port)) = s.accept()
        newthread = ClientThread(ip, port, clientsock)
        newthread.start()
