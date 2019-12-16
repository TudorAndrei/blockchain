from time import time
import json
from uuid import uuid4
from textwrap import dedent
import hashlib
from urllib.parse import urlparse
import requests


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transaction = []
        self.nodes = set()
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        """
        Creates a new Block in the Blockchain
        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dic> New Block
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transaction,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transaction = []
        return block
        

    def new_transaction(self, sender, recipient, amount):
        """
        Create a new transaction to go into the next minded Block
        :param sender: <str> Adress of the Sender
        :param recipient: <str> Adress of the Recipient
        :param amount: <int> The index of the Block that will hold the new transaction 
        """
        self.current_transaction.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        """
        Create a SHA-256 hash of a Block
        :param block: <dict> Block
        :return: <str>
        """
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Validate the Proof:
            Hash(last_proof, proof) contains 4 leading 0?
        :param last_proof: <int> Previous proof
        :param proof: <int> Current proof
        :return: <bool> The truth state of the evaluation
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def register_node(self, adress):
        """
        Adds a new node to the list of nodes
        :param adress: <str> Adress of node.
        :return: None
        """
        parsed_url = urlparse(adress)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        """
        Determines if the blockchain is valid
        :param chain: <list> A blockchain
        :return: <bool> The validity of the blockchain
        """

        last_block = chain[0]
        index = 1;
        while index < len(chain):
            block = chain[index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n===========\n")
            
            if block['previous_hash'] != self.hash(last_block)last_block
                return False
            
            if not self.valid_proof(last_block['proof'], block['proof'])
                return False
            
            last_block = block
            index += 1
        
        return True

    def resolve_conflict(self):
        """
        Consensuls algorithm that solves conflicts, by replacing our chan
        with the longest one in the network
        :return: <bool> True if the chain was replaced
        """
        neighbour = self.nodes
        new_chain = None

        max_len = len(self.chain)
        for node in neighbour:
            response = requests.get(f'https://{node}/chain')
            
            if response.status_code == 200:
                chain = response.json()['chain']
                len = response.json()['length']

                if len > max_len and self.valid_chain(chain):
                    max_len = len
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True
        
        return False
