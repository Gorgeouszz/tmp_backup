from hashlib import sha256
import json
import time
import threading 
from threading import Lock,Thread
import random

from flask import Flask, request
import requests

time_interval = 10

class Genesis_port:
    def __init__(self,timestamp):
        self.timestamp = timestamp
        self.DAG = []
        genesis1 = Vertex("hash_","pre","pre",True,1,0,timestamp)
        self.DAG.append(genesis1)
    def add_TX(self,ver):
        if ver not in self.DAG:
            tmp = ver
            tmp.next = []
        flag1 = False
        flag2 = False
        for i in self.DAG: #
            if tmp.pre1 == i:
                PRE1 = tmp.pre1
                flag1 = True
            if tmp.pre2 == i:
                PRE2 = tmp.pre2
                flag2 = True
        if flag1 & flag2:   #
            PRE1.next.append(tmp)
            PRE2.next.append(tmp)
            self.DAG.append(tmp)
            #change_weight(tmp,tmp.weight)

    def package(self):
        print("package+++")
        transaction = []
        print(len(self.DAG))
        for i in self.DAG:
            tx_data = "{u'content': u'"+"pre1="+str(i.pre1)+"      pre2="+str(i.pre2)+ "', 'timestamp': "+str(i.time)+", u'author': u'"+"hash = "+i.hash_+"'}"
            tx_ = eval(tx_data)
            transaction.append(tx_)
            #if i not in transaction:
                #transaction.append(str(i.time))
                #content__ =  str(i.time)+"DAG_TX"
                #tx_data = "{u'content': u'123', 'timestamp': 1602122174.492177, u'author': u'123'}"
                #tx_data = "{u'content': u'"+content__ +"', 'timestamp': 1602122174.492177, u'author': u'123'}"
                #tx_data = "{u'content': u"+content__ +", 'timestamp': "+"str(time.time())"+", u'author': u'sender'}"
                #tx_data = "{u'content': u'123', 'timestamp': "+str(time.time())+", u'author': u'123'}"
                # tx_data = "{u'content': u'"+"pre1="+str(i.pre1)+"      pre2="+str(i.pre2)+ "', 'timestamp': "+str(i.time)+", u'author': u'"+"hash = "+i.hash_+"'}"
                # tx_ = eval(tx_data)
                # transaction.append(tx_)
        print(transaction)
        print(type(transaction))
        print("transaction len",len(transaction))
        return transaction


    def compute_hash(self):
        """
        A function that return the hash of the block contents.
        """
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()


class Vertex:
    def __init__(self,hash_,pre1,pre2,flag,weight,accumulate,time):
        self.hash_ = hash_
        self.connectedTo = []
        self.pre1 = pre1
        self.pre2 = pre2
        self.flag = flag
        self.next = []
        self.weight = weight
        self.accumulate = accumulate
        self.time = time



class Block:
    def __init__(self, index, transactions, timestamp, previous_hash,genesis_port ,nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.genesis_port = genesis_port

    def compute_hash(self):
        """
        A function that return the hash of the block contents.
        """

        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()


class Blockchain:
    # difficulty of our PoW algorithm
    difficulty = 3

    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []
        self.DAG = []

    def create_genesis_block(self):
        """
        A function to generate genesis block and appends it to
        the chain. The block has index 0, previous_hash as 0, and
        a valid hash.
        """
        port1 = time.time()+3
        port2 = time.time()+time_interval+3
        port3 = time.time()+2*time_interval+3
        genesis_block0 = Block(0, [], 0, "0",port1)
        genesis_block0.hash = genesis_block0.compute_hash()
        genesis_block1 = Block(1, [], 0,genesis_block0.hash ,port2)
        genesis_block1.hash = genesis_block1.compute_hash()
        genesis_block2 = Block(2, [], 0,genesis_block1.hash ,port3)
        genesis_block2.hash = genesis_block2.compute_hash()
        self.chain.append(genesis_block0)
        self.chain.append(genesis_block1)
        self.chain.append(genesis_block2)
        for i in blockchain.chain:
            if i.genesis_port > time.time():
                tmp = Genesis_port(i.genesis_port)
                self.DAG.append(tmp)


    @property
    def last_block(self):
        return self.chain[-1]

    def add_block(self, block, proof):
        """
        A function that adds the block to the chain after verification.
        Verification includes:
        * Checking if the proof is valid.
        * The previous_hash referred in the block and the hash of latest block
          in the chain match.
        """
        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            return False

        if not Blockchain.is_valid_proof(block, proof):
            return False

        block.hash = proof
        self.chain.append(block)
        return True

    @staticmethod
    def proof_of_work(block):
        """
        Function that tries different values of nonce to get a hash
        that satisfies our difficulty criteria.
        """
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()

        return computed_hash

    def add_new_transaction(self,genesis_port,transaction):
        genesis_port.add_TX(transaction)

    @classmethod
    def is_valid_proof(cls, block, block_hash):
        """
        Check if block_hash is valid hash of block and satisfies
        the difficulty criteria.
        """
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.compute_hash())

    @classmethod
    def check_chain_validity(cls, chain):
        result = True
        previous_hash = "0"

        for block in chain:
            block_hash = block.hash
            # remove the hash field to recompute the hash again
            # using `compute_hash` method.
            delattr(block, "hash")

            if not cls.is_valid_proof(block, block_hash) or \
                    previous_hash != block.previous_hash:
                result = False
                break

            block.hash, previous_hash = block_hash, block_hash

        return result

    def mine(self,genesis_port):
        """
        This function serves as an interface to add the pending
        transactions to the blockchain by adding them to the block
        and figuring out Proof Of Work.
        """
        if not genesis_port.DAG:
            print("no transaction")
            return False
        # test = eval("{u'content': u'123', 'timestamp': "+str(time.time())+", u'author': u'123'}")
        last_block = self.last_block
        new_port = time.time()+2*time_interval
        timestamp_ = time.time()
        new_block = Block(index=last_block.index + 1,
                          transactions=genesis_port.package(),
                          #transactions=[],
                          timestamp=timestamp_,
                          previous_hash=last_block.hash,
                          genesis_port=new_port)
        proof = self.proof_of_work(new_block)
        
        self.add_block(new_block, proof)
        print("DAG append")
        blockchain.DAG.append(Genesis_port(new_port))
        blockchain.DAG.pop(0)
        if blockchain.DAG[0].timestamp > timestamp_:
            blockchain.DAG[0].timestamp = timestamp_

        return True


app = Flask(__name__)

# the node's copy of blockchain
blockchain = Blockchain()
blockchain.create_genesis_block()

# the address to other participating members of the network
peers = set()


# endpoint to submit a new transaction. This will be used by
# our application to add new data (posts) to the blockchain





#need rebuild






@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    tx_data = request.get_json()
    required_fields = ["author", "content","pre1","pre2"]

    for field in required_fields:
        if not tx_data.get(field):
            return "Invalid transaction data", 404

    flag1 = False
    flag2 = False
    for i in blockchain.DAG:
        for j in i.DAG:
            if j.hash_ == tx_data['pre1']:
                flag1 = True
            if j.hash_ == tx_data['pre2']:
                flag2 = True
            if flag1 & flag2:
                i.add_TX(tx_data)
            


    blockchain.add_new_transaction(tx_data)

    return "Success", 201


# endpoint to return the node's copy of the chain.
# Our application will be using this endpoint to query
# all the posts to display.
@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data,
                       "peers": list(peers)})


# endpoint to request the node to mine the unconfirmed
# transactions (if any). We'll be using it to initiate
# a command to mine from our application itself.
@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    return "no use"

# endpoint to add new peers to the network.
@app.route('/register_node', methods=['POST'])
def register_new_peers():
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    # Add the node to the peer list
    peers.add(node_address)

    # Return the consensus blockchain to the newly registered node
    # so that he can sync
    return get_chain()


@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
    """
    Internally calls the `register_node` endpoint to
    register current node with the node specified in the
    request, and sync the blockchain as well as peer data.
    """
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400
    #print("request.get_json()['node_address']",request.get_json()["node_address"])
    #peers.update(str(node_address+'/'))
    data = {"node_address": request.host_url}
    headers = {'Content-Type': "application/json"}

    # Make a request to register with remote node and obtain information
    response = requests.post(node_address + "/register_node",
                             data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        #global blockchain
        #global peers
        # update chain and the peers
        chain_dump = response.json()['chain']
        #blockchain = create_chain_from_dump(chain_dump)
        #http://127.0.0.1:8001/
        #peers.update('http://127.0.0.1:8002/')
        #peers.update(response.json()['peers'])
        #print("response.json()['peers']",response.json()['peers'])
        peers.add(node_address+'/')
        return "Registration successful", 200
    else:
        # if something goes wrong, pass it on to the API response
        return response.content, response.status_code









#need rebuild









def create_chain_from_dump(chain_dump):
    generated_blockchain = Blockchain()
    generated_blockchain.create_genesis_block()
    for block_data in chain_dump:
        block = Block(block_data["index"],
                      block_data["transactions"],
                      block_data["timestamp"],
                      block_data["previous_hash"],
                      block_data["genesis_port"])
                      #block_data["nonce"])
        proof = block_data['hash']
        added = generated_blockchain.add_block(block, proof)
        if not added:
            print("The chain dump is tampered!!")
            raise Exception("The chain dump is tampered!!")
    return generated_blockchain








#need rebuild











# endpoint to add a block mined by someone else to
# the node's chain. The block is first verified by the node
# and then added to the chain.
@app.route('/add_block', methods=['POST'])
def verify_and_add_block():
    block_data = request.get_json()
    block = Block(block_data["index"],
                  block_data["transactions"],
                  block_data["timestamp"],
                  block_data["previous_hash"],
                  block_data["genesis_port"])
                  #block_data["nonce"])

    proof = block_data['hash']
    added = blockchain.add_block(block, proof)

    if not added:
        return "The block was discarded by the node", 400

    return "Block added to the chain", 201


# endpoint to query unconfirmed transactions
@app.route('/pending_tx')
def get_pending_tx():
    return "no use"


def consensus():
    """
    Our naive consnsus algorithm. If a longer valid chain is
    found, our chain is replaced with it.
    """
    global blockchain

    longest_chain = None
    current_len = len(blockchain.chain)

    for node in peers:
        response = requests.get('{}chain'.format(node))
        length = response.json()['length']
        chain = response.json()['chain']
        if length > current_len and blockchain.check_chain_validity(chain):
            current_len = length
            longest_chain = chain

    if longest_chain:
        blockchain = longest_chain

        return True

    return False


def announce_new_block(block):
    """
    A function to announce to the network once a block has been mined.
    Other blocks can simply verify the proof of work and add it to their
    respective chains.
    """
    for peer in peers:
        print("peer = ",peer)
        url = "{}add_block".format(peer)
        headers = {'Content-Type': "application/json"}
        requests.post(url,
                      data=json.dumps(block.__dict__, sort_keys=True),
                      headers=headers)

# Uncomment this line if you want to specify the port number in the code
app.run(debug=True, port=8004)


class Mythread(threading.Thread):
    def __init__(self):
        super(Mythread, self).__init__()
    def run(self):
        global blockchain
        global tx_test
        global flag
        num = 0
        while True:
            time.sleep(3)
            content_ = "'the " +str(num) +" TX'"
            num = num + 1
            time.sleep(0.5)
            print("test")
            #tx_ = {u'content': u'123', 'timestamp': 1602122174.492177, u'author': u'123'}
            #tx_1 = "{u'content': u'123', 'timestamp': "+str(time.time())+", u'author': u'123'}"
            tx_1 = "{u'content': u"+content_+", 'timestamp': "+str(time.time())+", u'author': u'node2'}"
            tx_ = eval(tx_1)
            blockchain.unconfirmed_transactions.append(tx_)

class Mythread_mine1(threading.Thread):
    def __init__(self):
        super(Mythread_mine1,self).__init__()
        global current_G
        current_G = []

    def run(self):
        
        global blockchain
        for i in blockchain.chain:
            if i.genesis_port > time.time():
                tmp = Genesis_port(i.genesis_port)
                current_G.append(tmp)
        for i in current_G:
            abcdefg = 0
            #print("G-list -------",i)
            
        while True: 

            if time.time() > current_G[1].timestamp:
                current_G.pop(0)
                #print("pop")
                for i in current_G:
                    abcdefg = 0
                    #print("pop-------",i)
            if blockchain.chain[-1].genesis_port != current_G[-1].timestamp:
                current_G.append(Genesis_port(blockchain.chain[-1].genesis_port))
                #print("add")
                for i in current_G:
                    abcdefg = 0
                    #print("add-------",i)

            #time.sleep(2)
            
            print("mine","len = ",len(current_G))
            while time.time() < current_G[1].timestamp:
                time.sleep(0.5)

            result = blockchain.mine(current_G[0])
            if not result:
                print("No transactions to mine")
            else:
                chain_length = len(blockchain.chain)
                consensus()
                if chain_length == len(blockchain.chain):
                    announce_new_block(blockchain.last_block)

class Mythread_mine(threading.Thread):
    def __init__(self):
        super(Mythread_mine,self).__init__()

    def run(self):
        global blockchain  
        for i in peers:
            print("peer = ",i)
        
      
        while True: 
            print("block chain len = ",len(blockchain.chain))
            time.sleep(15)
            result = blockchain.mine(blockchain.DAG[0])
            #print("block++++++++++++++++++++++")
            if not result:
                print("No transactions to mine")
            chain_length = len(blockchain.chain)
            consensus()
            if chain_length == len(blockchain.chain):
                announce_new_block(blockchain.last_block)

class add_DAGTX(threading.Thread):
    def __init__(self):
        super(add_DAGTX,self).__init__() 
    def run(self):
        global current_G
        global blockchain

        while True:
            time.sleep(3)
            print("DAG_len = ",len(blockchain.DAG))
            print("Add DAG tx")
            tip = []
            for i in blockchain.DAG[0].DAG:
                if not i.next:
                    tip.append(i)

            if len(tip) == 1:
                PRE1 = tip[0]
                PRE2 = tip[0]
            else:
                while True:
                    a = random.randint(0,len(tip)-1)
                    b = random.randint(0,len(tip)-1)
                    if a != b:
                        break
                PRE1 = tip[a]
                PRE2 = tip[b]
            new_tx = Vertex("hash_",PRE1,PRE2,True,1,0,time.time())
            blockchain.DAG[0].add_TX(new_tx)
            print(len(blockchain.DAG))

class add_DAGTX_test(threading.Thread):
    def __init__(self):
        super(add_DAGTX_test,self).__init__() 
    def run(self):
        global current_G
        global blockchain
        index = 0
        while True:
            index += 1
            time.sleep(3)
            print("DAG_len = ",len(blockchain.DAG))
            print("Add DAG tx")
            tip = []
            for i in blockchain.DAG[0].DAG:
                if not i.next:
                    tip.append(i)

            if len(tip) == 1:
                PRE1 = tip[0]
                PRE2 = tip[0]
            else:
                while True:
                    a = random.randint(0,len(tip)-1)
                    b = random.randint(0,len(tip)-1)
                    if a != b:
                        break
                PRE1 = tip[a]
                PRE2 = tip[b]
            new_tx = Vertex("hash_",PRE1,PRE2,True,1,0,time.time())
            tx_content = "index =" + str(index)
            tx_data = "{u'content': u'"+tx_content+"', 'timestamp': "+str(time.time())+", u'author': u'sender',"+"u'pre1': u'"+PRE1.hash_+"',u'pre2': u'"+PRE2.hash_+"'}"
            print(tx_data)
            peer1 = u'http://127.0.0.1:8001/'
            peer2 = u'http://127.0.0.1:8002/'
            peer3 = u'http://127.0.0.1:8003/'
            peers = [peer1, peer2,peer3]
            for i in peers:
                url = "{}new_transaction".format(i) 
                headers = {'Content-Type': "application/json"}
                requests.post(url,
                data = json.dumps(eval(tx_data)),
                headers = headers )
            print(len(blockchain.DAG))
             


'''
T1 = Mythread()
T1.start()

T2 = Mythread_mine()
T2.start()
'''
T3 = add_DAGTX_test()
T3.start()
time.sleep(5)
#print("result ================ ",len(create_chain_from_dump(blockchain.chain)))

