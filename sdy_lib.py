# -*- coding: utf-8 -*-
import threading
import bitcoin
import hashlib
import random
import pickle
import time
import os

class Blockchain :
    def __init__(self) :
        self.chain = []

    def add_block(self, block) :
        self.chain.append(block)

    def get_last_block(self) :
        return self.chain[-1]

    def get_chain_length(self) :
        return len(self.chain)

class Block :
    def __init__(self, proof=None, previous_hash=None) :

        #self.index = len(self.chain) + 1
        self.timestamp = time.time()
        self.proof = proof
        self.block_hash = None
        self.previous_hash = previous_hash
        self.transaction = []

    def add_transaction(self, transaction) :
        #on rajoutera des tests sur l'AUTHENTICité de la transaction
        self.transaction.append(transaction)

class Miner :

    def __init__(self, block):
        self.list_of_utxo = []
        self.temp_transaction = []
        self.block = block
        self.list_of_other_miners = []

    def available_utxo(self) :
        self.list_of_utxo = []
        for transaction in self.block.transaction :
            for i in transaction.senders :
                if i in self.list_of_utxo :
                    self.list_of_utxo.remove(i)
            for j in range(len(transaction.recipients)) :
                self.list_of_utxo.append((transaction.transaction_hash, j))

    def get_transaction_by_hash(self, hash) :
        for transaction in self.block.transaction :
            if hash == transaction.transaction_hash :
                return transaction
        return 'transaction not found' # gros bordel en cas d'erreur

    def get_utxo_by_address(self, address) :
        list_of_wallet_utxo = []
        for source in self.list_of_utxo :
            hash, index = source
            transaction = self.get_transaction_by_hash(hash)
            if transaction.recipients[index][0] == address :
                amount = transaction.recipients[index][1]
                list_of_wallet_utxo.append((source, amount))
        return list_of_wallet_utxo

    def create_transaction_hash(self, transaction) :
        senders_str = ''
        for i in transaction.senders :
            senders_str += i[0] + str(i[1])
        recipients_str = ''
        for i in transaction.recipients :
            recipients_str += i[0] + str(i[1])
        transaction_hash = hashlib.sha256(senders_str.encode('utf-8') + recipients_str.encode('utf-8') + transaction.public_key.encode('utf-8')).hexdigest()
        return transaction_hash

    def are_senders_authentics(self, transaction) :
        try :
            if len(transaction.senders) == 0 :
                are_authentics = False
            else :
                are_authentics = True
            for source in transaction.senders :
                hash, index = source
                previous_transaction = self.get_transaction_by_hash(hash)
                if source not in self.list_of_utxo or previous_transaction.recipients[index][0] != bitcoin.pubkey_to_address(transaction.public_key) or previous_transaction.recipients[index][1] < 0 :
                    are_authentics = False
        except :
            are_authentics = False
        finally :
            return are_authentics

    def is_output_lessthan_or_equalto_input(self, transaction) :
        try :
            is_inout_valid = False
            input_amount = 0
            for source in transaction.senders :
                hash, index = source
                previous_transaction = self.get_transaction_by_hash(hash)
                input_amount += previous_transaction.recipients[index][1]

            output_amount = 0
            for recipient in transaction.recipients :
                address, amount = recipient
                output_amount += amount
            if input_amount >= output_amount :
                is_inout_valid = True
        except :
            is_inout_valid = False
        finally :
            return is_inout_valid

    def are_recipients_authentics(self, transaction) :
        try :
            are_authentics = True
            for recipient in transaction.recipients :
                address, amount = recipient
                if amount < 0 :
                    are_authentics = False
        except :
            are_authentics = False
        finally :
            return are_authentics

    def is_signature_authentic(self, transaction) :
        try :
            is_valid = False
            hash = self.create_transaction_hash(transaction)
            if bitcoin.ecdsa_verify(hash, transaction.signature, transaction.public_key) :
                is_valid = True
        except :
            is_valid = False
        finally :
            return is_valid

    def verify_transaction(self, transaction) :
        #print("authentics sources", self.are_senders_authentics(transaction))
        #print("output is less than or equal to input", self.is_output_lessthan_or_equalto_input(transaction))
        #print("authentics recipients", self.are_recipients_authentics(transaction))
        #print("authentics signature", self.is_signature_authentic(transaction))
        if self.are_senders_authentics(transaction) and self.is_output_lessthan_or_equalto_input(transaction) and self.are_recipients_authentics(transaction) and self.is_signature_authentic(transaction) :
            print("AUTHENTIC")
            return True
        else :
            print("NOT AUTHENTIC")
            return False

    def verify_temp_transaction_list(self) :
        self.available_utxo()
        for transaction in self.temp_transaction :
            if self.verify_transaction(transaction) :
                self.block.add_transaction(transaction)
                for source in transaction.senders :
                    self.list_of_utxo.remove(source)
        self.temp_transaction = []


class ClientThread(threading.Thread):

    def __init__(self, miner, ip, port, socket):
        threading.Thread.__init__(self)
        self.miner = miner
        self.ip = ip
        self.port = port
        self.socket = socket
        self.lock = threading.Lock()
        print("[+] New thread started for " + self.ip + ":"+ str(self.port))

    def run(self):
        print("Connection from : " + self.ip + ":" + str(self.port))

        data = "dummydata"

        while True:
            if not data :
                break
            data = self.socket.recv(1024)
            command = data.decode('utf-8')

            if command == 'get_sold' :
                self.get_sold()
            elif command == 'send_sdy' :
                self.send_sdy()
            else :
                print(command + ' unknown command')

        self.socket.close()
        print("Client disconnected...")

    def socket_send(self, packet) :
        pickled_packet = pickle.dumps(packet)
        self.socket.send(pickled_packet)

    def socket_recv(self, size) :
        pickled_packet = self.socket.recv(size)
        packet = pickle.loads(pickled_packet)
        return packet

    def get_sold(self) :
        self.miner.available_utxo()
        address = self.socket_recv(1048576)
        with self.lock :
            list_of_wallet_utxo = self.miner.get_utxo_by_address(address)
        self.socket_send(list_of_wallet_utxo)

    def send_sdy(self) :
        self.miner.available_utxo()
        transaction = self.socket_recv(1048576)
        with self.lock :
            self.miner.temp_transaction.append(transaction)
            self.miner.verify_temp_transaction_list()


class Transaction :
    def __init__(self, senders, recipients, public_key) :
        self.senders = senders
        self.recipients = recipients
        self.signature = None
        self.public_key = public_key
        self.create_hash()

    def create_hash(self) :
        senders_str = ''
        for i in self.senders :
            senders_str += i[0] + str(i[1])
        recipients_str = ''
        for i in self.recipients :
            recipients_str += i[0] + str(i[1])
        self.transaction_hash = hashlib.sha256(senders_str.encode('utf-8') + recipients_str.encode('utf-8') + self.public_key.encode('utf-8')).hexdigest()

class Wallet :
    def __init__(self) :
        self.create_keys()
        self.sold = 0
        self.my_utxo = []
        self.my_utxo_value = []

    def create_keys(self) :
        valid_private_key = False
        while not valid_private_key:
            #creation de la private_key
            self.private_key = bitcoin.random_key()
            #conversion de la private_key de l'hex à decimal
            self.decoded_private_key = bitcoin.decode_privkey(self.private_key, 'hex')
            #on sort de la boucle si la cle correspond aux critères
            valid_private_key = 0 < self.decoded_private_key < bitcoin.N

        #creation de la wif_encoded_private_key
        self.wif_encoded_private_key = bitcoin.encode_privkey(self.decoded_private_key, 'wif')
        #creation de la private_key compressée
        self.compressed_private_key = self.private_key + '01'
        #creation de wif_compressed_private_key
        self.wif_compressed_private_key = bitcoin.encode_privkey(bitcoin.decode_privkey(self.compressed_private_key, 'hex'), 'wif_compressed')
        #creation de la public_key
        self.public_key = bitcoin.fast_multiply(bitcoin.G, self.decoded_private_key)
        #enc'previous_transaction': previous_transaction,odage en hexa decimal avec 04 comme prefixe de la public_key
        self.hex_encoded_public_key = bitcoin.encode_pubkey(self.public_key, 'hex')
        #compression de la public_key, ajout du prefixe pair ou impaire
        (self.public_key_x, self.public_key_y) = self.public_key
        self.compressed_prefix = '02' if (self.public_key_y % 2) == 0 else '03'
        self.hex_compressed_public_key = self.compressed_prefix + (bitcoin.encode(self.public_key_x, 16).zfill(64))

        #cre'previous_transaction': previous_transaction,ation de l'adresse bitcoin
        self.address = bitcoin.pubkey_to_address(self.public_key)
        #creation de l'adresse compressée
        self.compressed_address = bitcoin.pubkey_to_address(self.hex_compressed_public_key)

    def get_my_utxo_from_miner(self, miner) :
        self.my_utxo = miner.get_utxo_by_address(self.address)

    def get_sold(self) :
        self.sold = 0
        for i in self.my_utxo :
            (transaction, index), amount = i
            self.sold += amount

    def save_wallet(self, file_name) :
        with open(file_name + '.scsw', 'wb') as tmp_file :
            pickle.dump(self, tmp_file, protocol=pickle.HIGHEST_PROTOCOL)
        print("saved " + file_name +'.scsw')

    def sign(self, message) :
        signature = bitcoin.ecdsa_sign(message, self.private_key)
        return signature

    def sign_my_transaction(self, recipients) :
        transaction_amount = 0
        for _, amount in recipients :
            transaction_amount += amount
        if transaction_amount > self.sold :
            print("Pas assez de fonds pour assurer la transaction, verifiez via un miner vos fonds, et ajoutez en si besoin")
        else :
            print("vous avez les fonds")
            current_funds = 0
            senders = []
            for utxo in self.my_utxo :
                source, funds = utxo
                current_funds += funds
                senders.append(source)
                if current_funds >= transaction_amount :
                    break
            if current_funds - transaction_amount > 0 :
                recipients.append((self.address, current_funds - transaction_amount))
            my_transaction = Transaction(senders, recipients, self.hex_encoded_public_key)
            my_transaction.signature = self.sign(my_transaction.transaction_hash)
            return my_transaction

    def send_transaction_to_miner(self, miner, recipients) :
        my_transaction = self.sign_my_transaction(recipients)
        miner.temp_transaction.append(my_transaction)

def list_wallets() :
    #creation d'une liste qui contiendra tous les wallets detectés dans le dossier
    list_of_wallets = []
    #on ajoute seulement les wallets à la liste
    for i in os.listdir() :
        if i.endswith('.scsw') :
            list_of_wallets.append(i)
    return list_of_wallets

def load_wallet(check_wallet=None) :
    if check_wallet == None :
        list_of_wallets = list_wallets()
        print(list_of_wallets)
        #on demande à l'utilisateur de selection un wallet valide
        wallet_is_valid = False
        while not wallet_is_valid :
            check_wallet = input("select your wallet\n>>")
            if check_wallet in list_of_wallets :
                wallet_is_valid = True
    #on ouvre le fichier selectionné, on recupère avec pickle l'objet
    with open(check_wallet, 'rb') as tmp_file :
        my_wallet = pickle.load(tmp_file)
    #on retourne l'objet
    return my_wallet

if __name__ == '__main__' :
    print('sdy lib')
