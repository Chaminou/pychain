
import socket
import time
import pickle
from sdy_lib import *

def get_sold() :
    pickled_address = pickle.dumps(wallet.address)
    s.send(pickled_address)
    pickled_list_of_wallet_utxo = s.recv(1048576)
    list_of_wallet_utxo = pickle.loads(pickled_list_of_wallet_utxo)
    wallet.my_utxo = list_of_wallet_utxo
    wallet.get_sold()
    print(wallet.my_utxo)
    print(wallet.sold)

def send_sdy() :
    recipient_address = input("Address of recipient\n>>")
    recipient_amount = int(input("Amount for the recipient\n>>"))
    transaction = wallet.sign_my_transaction([(recipient_address, recipient_amount)])
    pickled_transaction = pickle.dumps(transaction)
    s.send(pickled_transaction)

if __name__ == '__main__' :

    host = '127.0.1.1'
    port = 4747

    s = socket.socket()
    while True :
        try :
            s.connect((host, port))
            break
        except :
            print('not connected to server, retrying every second')
            time.sleep(1)

    print("Connected to ", host)

    wallet = load_wallet('bob.scsw')

    while True :

        # alice address : 19HB4ECfCoGsiwzDWpGDVEwBpkg83b2q5v
        # bob address : 14LRGBn94deQNE4eEG8F2ve7rmyoEATKw4

        input_command = str.encode(input(">>"))
        s.send(input_command)
        command = input_command.decode('utf-8')

        time.sleep(0.1)
        if command == 'get_sold' :
            get_sold()
        elif command == 'send_sdy' :
            send_sdy()
        elif command == 'quit' :
            quit()
        else :
            print(command + ' unknown command')
