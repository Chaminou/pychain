
import socket
import time
import pickle
from sdy_lib import *

def get_sold() :
    pickled_address = c.recv(1048576)
    miner.available_utxo()
    address = pickle.loads(pickled_address)
    list_of_wallet_utxo = miner.get_utxo_by_address(address)
    pickled_list_of_wallet_utxo = pickle.dumps(list_of_wallet_utxo)
    c.send(pickled_list_of_wallet_utxo)

def send_sdy() :
    pickled_transaction = c.recv(1048576)
    transaction = pickle.loads(pickled_transaction)
    miner.temp_transaction.append(transaction)
    print(miner.list_of_utxo)
    miner.verify_temp_transaction_list()
    print(miner.list_of_utxo)

if __name__ == "__main__" :


    host = '127.0.1.1'
    port = 5000

    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))

    block = Block()
    miner =  Miner(block)
    first_transaction = Transaction([('None', None)], [('19HB4ECfCoGsiwzDWpGDVEwBpkg83b2q5v', 100), ('14LRGBn94deQNE4eEG8F2ve7rmyoEATKw4', 100)], 'None')
    block.add_transaction(first_transaction)

    while True :
        s.listen(1)
        c, addr = s.accept()
        print("Connection from :", str(addr))

        while True :
            data = c.recv(1024)
            if not data :
                break
            command = data.decode(encoding='UTF-8')

            #miner.available_utxo()

            if command == 'get_sold' :
                get_sold()
            elif command == 'send_sdy' :
                send_sdy()
            else :
                print(command + ' unknown command')
