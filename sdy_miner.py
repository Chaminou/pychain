
import time
import socket
import pickle
import threading
from sdy_lib import *

if __name__ == "__main__" :

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
        newthread = ClientThread(miner, ip, port, clientsock)
        newthread.start()
