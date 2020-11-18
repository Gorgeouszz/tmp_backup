from hashlib import sha256
import json
import time
import threading 
from threading import Lock,Thread
import random

from flask import Flask, request
import requests

time_interval = 10
interrupt = False
dict_ = {'0':"0000" ,'1':"0001" ,'2':"0010" ,'3':"0011" ,'4':"0100" ,'5':"0101" ,'6':"0110",'7':"0111",'8':"1000",'9':"1001",'a':"1010",'b':"1011",'c':"1100",'d':'1101','e':"1110",'f':"1111"}

class Genesis_port:
    def __init__(self,timestamp):
        self.timestamp = timestamp
        self.DAG = []
        genesis01 = Vertex("hash_","pre","pre",True,1,0,timestamp)
        genesis02 = Vertex("hash_","pre","pre",True,1,0,timestamp)
        genesis1 = Vertex(str(len(blockchain.chain)+1),genesis01,genesis02,True,1,0,timestamp)
        self.DAG.append(genesis1)
    def add_TX(self,ver):
        if ver not in self.DAG:
            tmp = ver
            tmp.next = []
        flag1 = False
        flag2 = False
        for i in self.DAG: #
            if tmp.pre1 == i.hash_:
                PRE1 = tmp.pre1
                flag1 = True
                PRE1 = i
            if tmp.pre2 == i.hash_:
                PRE2 = tmp.pre2
                flag2 = True
                PRE2 = i
        if flag1 & flag2:   #
            PRE1.next.append(tmp.hash_)
            PRE2.next.append(tmp.hash_)
            self.DAG.append(tmp)
        else:
            self.DAG.append(tmp)

    def package(self):
        transaction = []
        for i in self.DAG:
            next_list = ''
            for j in i.next:
                next_list += str(j)
            tx_data = "{u'content': u'"+i.hash_+ "', 'timestamp': "+str(i.time)+", u'author': u'test_node',u'pre1':u'"+str(i.pre1)+"',u'pre2':u'"+str(i.pre2)+"',u'next':'"+next_list+"'}"
            tx_ = eval(tx_data)
            transaction.append(tx_)
        return transaction


    def compute_hash(self):
        """
        A function that return the hash of the block contents.
        """
        block_string = json.dumps(self.__dict__, sort_keys=True)
        tmp_hash = sha256(block_string.encode()).hexdigest()
        result = ''
        for i in tmp_hash:
            result += dict_[i]
        return result


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
        tmp_hash = sha256(block_string.encode()).hexdigest()
        result = ''
        for i in tmp_hash:
            result += dict_[i]
        return result


class Blockchain:
    # difficulty of our PoW algorithm
    difficulty = 18

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
        genesis_block0.hash = self.proof_of_work(genesis_block0)
        genesis_block1 = Block(1, [], 0,genesis_block0.hash ,port2)
        genesis_block1.hash = self.proof_of_work(genesis_block1)
        genesis_block2 = Block(2, [], 0,genesis_block1.hash ,port3)
        genesis_block2.hash = self.proof_of_work(genesis_block2)
        self.chain.append(genesis_block0)
        self.DAG.append(Genesis_port(port1))
        self.chain.append(genesis_block1)
        self.DAG.append(Genesis_port(port2))
        self.chain.append(genesis_block2)  
        self.DAG.append(Genesis_port(port3))

#        for i in blockchain.chain:
#            if i.genesis_port > time.time():
#                tmp = Genesis_port(i.genesis_port)
#                self.DAG.append(tmp)


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

        # f = open("error.txt",mode="a")
        # f.write("{}\r\n{}\r\n\r\n{}\r\n{}".format(previous_hash,block.previous_hash,block.compute_hash(),proof)) 
        # f.close()
        if previous_hash != block.previous_hash:
            return False

        if not Blockchain.is_valid_proof(block, proof):
            return False

        block.hash = proof
        self.chain.append(block)
        return True

    @staticmethod
    def proof_of_work(block):
        global interrupt
        """
        Function that tries different values of nonce to get a hash
        that satisfies our difficulty criteria.
        """
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
            if interrupt == True:
                return computed_hash

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
        
        i = 0
        for block_ in chain:
            
            if i < 3:
                i+=1
                continue
            block = Block(block_['index'], block_['transactions'],block_['timestamp'],block_['previous_hash'], block_['genesis_port'],block_['nonce'])
            block_hash = block_['hash']
            # remove the hash field to recompute the hash again
            # using `compute_hash` method.
            #delattr(block, "hash")
            if not cls.is_valid_proof(block, block_hash):
                result = False
                break
            block.hash, previous_hash = block_hash, block_hash
        return result

    def mine(self,genesis_port):
        global interrupt

        """
        This function serves as an interface to add the pending
        transactions to the blockchain by adding them to the block
        and figuring out Proof Of Work.
        """
        
        if not genesis_port.DAG:
            return False
        last_block = self.last_block
        new_port = time.time()+2*time_interval
        timestamp_ = time.time()
        new_block = Block(index=last_block.index + 1,
                          transactions=genesis_port.package(),
                          timestamp=timestamp_,
                          previous_hash=last_block.hash,
                          genesis_port=new_port)
        proof = self.proof_of_work(new_block)
        if interrupt == True:
            interrupt = False
            return False        
        self.add_block(new_block, proof)
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
    # f = open("log1.txt",mode = "a")
    # #f.write("%s %d" %blockchain.DAG[0].DAG[0].hash_ %len(blockchain.DAG[0].DAG))
    # f.write("{} {}".format(blockchain.DAG[0].DAG[0].hash_,len(blockchain.DAG[0].DAG)))
    # f.write("\r\n")
    tx_data = request.get_json()
    required_fields = ["author", "content","pre1","pre2"]

    flag1 = False
    flag2 = False  
    for i in blockchain.DAG[1:]:
        for j in i.DAG:
            if j.hash_ == tx_data['pre1']:
                pre1 = j
                flag1 = True
            if j.hash_ == tx_data['pre2']:
                pre2 = j
                flag2 = True
            if flag1 & flag2:
                tx_hash = tx_data['content']
                tx_data_ = Vertex(tx_hash, tx_data['pre1'], tx_data['pre2'],True,1,0,tx_data['timestamp'])
                pre1.next = tx_data_.hash_
                pre2.next = tx_data_.hash_
                i.DAG.append(tx_data_)
                break

        if flag1 & flag2:
            break

    if not flag1 & flag2:

        return "Invalid transaction data", 404
            


    #blockchain.add_new_transaction(tx_data)

    return "Success", 201


# endpoint to return the node's copy of the chain.
# Our application will be using this endpoint to query
# all the posts to display.
@app.route('/chain', methods=['GET'])
def get_chain():
    global blockchain
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data,
                       "peers": list(peers)})


# endpoint to request the node to mine the unconfirmed
# transactions (if any). We'll be using it to initiate(block.__dict__
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
    #peers.add(node_address)
    #data = {"node_address": request.host_url}
    #headers = {'Content-Type': "application/json"}
    #response = requests.post(node_address + "/register_node",
    #data=json.dumps(data), headers=headers)    
    #peers.update(response.json()['peers'])
    # Return the consensus blockchain to the newly registered node
    # so that he can sync
    peers.add(node_address)
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
    data = {"node_address": request.host_url}
    headers = {'Content-Type': "application/json"}

    # Make a request to register with remote node and obtain information
    response = requests.post(node_address + "/register_node",
                             data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        peers.add(node_address+'/')
        return "Registration successful", 200
    else:
        # if something goes wrong, pass it on to the API response
        return response.content, response.status_code


def create_chain_from_dump(chain_dump):
    generated_blockchain = Blockchain()
    generated_blockchain.create_genesis_block()
    for block_data in chain_dump:
        block = Block(block_data["index"],
                      block_data["transactions"],
                      block_data["timestamp"],
                      block_data["previous_hash"],
                      block_data["genesis_port"])
        proof = block_data['hash']
        added = generated_blockchain.add_block(block, proof)
        if not added:
            print("The chain dump is tampered!!")
            raise Exception("The chain dump is tampered!!")
    return generated_blockchain




# endpoint to add a block mined by someone else to
# the node's chain. The block is first verified by the node
# and then added to the chain.
@app.route('/add_block', methods=['POST'])
def verify_and_add_block():
    global interrupt
    interrupt =True
    block_data = request.get_json()
    block = Block(block_data["index"],
                  block_data["transactions"],
                  block_data["timestamp"],
                  block_data["previous_hash"],
                  block_data["genesis_port"],
                  block_data["nonce"])

    proof = block_data['hash']
    f = open("error.txt",mode="a")
    f.write("input block = {}".format(block.compute_hash()))
    f.close()
    added = blockchain.add_block(block, proof)


    if not added:
        return "The block was discarded by the node", 400
    blockchain.DAG.pop(0)
    blockchain.DAG.append(Genesis_port(block_data["genesis_port"]))
    if blockchain.DAG[0].timestamp > block_data["timestamp"]:
        blockchain.DAG[0].timestamp = block_data["timestamp"]
    return "Block added to the chain", 201


# endpoint to query unconfirmed transactions
@app.route('/pending_tx')
def get_pending_tx():
    block_data = request.get_json()

    return "no use"

def send_DAG():
    global blockchain
    for peer in peers:
        url = "{}pending_tx".format(peer)
        headers = {'Content-Type': "application/json"}
        requests.post(url,
                      data=json.dumps(blockchain.DAG.__dict__, sort_keys=True),
                      headers=headers)
        

def consensus():
    """
    Our naive consnsus algorithm. If a longer valid chain is
    found, our chain is replaced with it.
    """
    global blockchain
    global interrupt
    longest_chain = None
    current_len = len(blockchain.chain)
    print("len(blockchain.chain)",len(blockchain.chain))
    for node in peers:

        response = requests.get('{}chain'.format(node))
        length = response.json()['length']
        chain = response.json()['chain']
        if length > current_len and blockchain.check_chain_validity(chain):
            current_len = length
            longest_chain = chain
    if longest_chain:
        blockchain.chain = []
        for block_ in longest_chain:
            block = Block(block_['index'], block_['transactions'],block_['timestamp'],block_['previous_hash'], block_['genesis_port'],block_['nonce'])
            block.hash = block_['hash']
            blockchain.chain.append(block)
        tmp_DAG = []
        tmp = []
        sum_tx = 0
        for i in blockchain.DAG:
            sum_tx += len(i.DAG)
        # f = open("transaction.txt",mode = "a")
        # f.write("befor len = %d" %sum_tx)
        for i in range(len(blockchain.DAG)):
            for j in blockchain.DAG[i].DAG:
                tmp.append(j)
            tmp_DAG.append(tmp)
            tmp = []
        blockchain.DAG = []
        for i in range(len(blockchain.chain)-3,len(blockchain.chain)):
            blockchain.DAG.append(Genesis_port(blockchain.chain[i].genesis_port))
        for i in range(3):
            blockchain.DAG[i].DAG[0].hash_ = str(len(blockchain.chain)+1-2+i)
        for i in range(len(blockchain.DAG)):
            for j in range(3):
                if blockchain.DAG[i].DAG[0].hash_ == tmp_DAG[j][0].hash_:
                    for k in  tmp_DAG[j][1:]:
                        blockchain.DAG[i].DAG.append(k)
        sum_tx_ = 0
        for i in blockchain.DAG:
            sum_tx_ += len(i.DAG)        
        # f.write("after len = %d \r\n" %sum_tx_)
        # f.close()
#把列表里的元素加到现在的DAG中
        interrupt = True           
        return True

    return False

def change_difficult():
    if len(blockchain.chain) > 15:
        sum_time = 0
        for i in range(len(blockchain.chain)-10,len(blockchain.chain)):
            sum_time += blockchain.chain[i].timestamp - blockchain.chain[i-1].timestamp
        sum_time = sum_time / 10
        print(sum_time)
        if sum_time < time_interval:
            if blockchain.difficulty < 28:
                blockchain.difficulty += 1
        else:
            blockchain.difficulty -= 1  


def announce_new_block(block):
    """
    A function to announce to the network once a block has been mined.
    Other blocks can simply verify the proof of work and add it to their
    respective chains.
    """

    for peer in peers:
        url = "{}add_block".format(peer)
        headers = {'Content-Type': "application/json"}
        requests.post(url,
                      data=json.dumps(block.__dict__, sort_keys=True),
                      headers=headers)

# Uncomment this line if you want to specify the port number in the code
app.run(debug=True, port=8001)


class Mythread(threading.Thread):
    def __init__(self):
        super(Mythread, self).__init__()
    def run(self):
        global blockchain
        num = 0
        while True:
            time.sleep(3)
            content_ = "'the " +str(num) +" TX'"
            num = num + 1
            time.sleep(0.5)
            tx_1 = "{u'content': u"+content_+", 'timestamp': "+str(time.time())+", u'author': u'node2'}"
            tx_ = eval(tx_1)
            blockchain.unconfirmed_transactions.append(tx_)



class Mythread_mine(threading.Thread):
    def __init__(self):
        super(Mythread_mine,self).__init__()
    def run(self):
        global blockchain  
        while True: 
            print("mine block ",len(blockchain.chain))
            #write mine message
            f = open("log1.txt",mode = "a")
            f.write("{}---".format(len(blockchain.chain)-1))
            f.write("mine = {} ".format(len(blockchain.chain[-1].transactions)))
            f.write("\r\n")
            f.close()

            #write transactions content
            f = open("node 1 log",mode = "a")
            for i in blockchain.chain:
                for j in i.transactions:
                    f.write("%s   " % j["content"])
                f.write("\r\n" )
            f.close()

            #write time message
            f = open("time.txt", mode="a")
            for i in blockchain.chain[3:]:
                for j in i.transactions[1:]:
                    time_ = i.timestamp - j["timestamp"]
                    #f.write("block time:%f   "%i.timestamp)
                    f.write("tx time:%f   "%j["timestamp"])
                    f.write("%f \r\n"%time_)
            f.close()
            result = blockchain.mine(blockchain.DAG[0])
            if not result:
                print("No transactions to mine")
                consensus()
                change_difficult()
                continue
            else:
                announce_new_block(blockchain.last_block)
                change_difficult()
                continue

class add_DAGTX(threading.Thread):
    def __init__(self):
        super(add_DAGTX,self).__init__() 
    def run(self):
        global current_G
        global blockchain

        while True:
            time.sleep(3)
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
            new_tx = Vertex("hash_",PRE1.hash_,PRE2.hash_,True,1,0,time.time())
            blockchain.DAG[0].add_TX(new_tx)

class typea(threading.Thread):
    def __init__(self):
        super(typea,self).__init__() 
    def run(self):             
        while True:
            # time.sleep(1)
            # print("DAG len :",len(blockchain.DAG))
            # print("DAG transaction",len(blockchain.DAG[1].DAG))
            # print("aaaaaaaaaaaa:",blockchain.DAG[1].DAG[0].hash_)
            # for i in blockchain.DAG:
            #     print(" ",i.timestamp)
            #     print(i.DAG[0].hash_)
            time.sleep(3)
            print("blockchain length = ",len(blockchain.chain))
            all_transactions = 0
            for i in blockchain.chain:
                all_transactions += len(i.transactions)
            print("all_transactions",all_transactions)
            for i in blockchain.DAG:
                print(i,"len = ",len(i.DAG))
            #print("DAG",len(blockchain.DAG[1].DAG))
            #print("DAG",blockchain.chain[len(blockchain.chain)-2].transactions)

class write_log(threading.Thread):
    def __init__(self):
        super(write_log,self).__init__() 
    def run(self):
        while True:
            time.sleep(5)
            if len(blockchain.chain) > 15 :
                # f = open("node 1 log",mode = "w")
                # for i in blockchain.chain:
                #     for j in i.transactions:
                #         f.write("%s   " % j["content"])
                #     f.write("\r\n" )
                # f.close()

                f = open("time.txt", mode="a")
                for i in blockchain.chain[3:]:
                    for j in i.transactions[1:]:
                        time_ = i.timestamp - j["timestamp"]
                        #f.write("block time:%f   "%i.timestamp)
                        f.write("tx time:%f   "%j["timestamp"])
                        f.write("%f \r\n"%time_)
                f.close()
                break


'''
T1 = Mythread()
T1.start()
'''



while len(blockchain.chain) <= 2:
    time.sleep(2)
T2 = Mythread_mine()
T2.start()




# T3 = typea()
# T3.start()

TW = write_log()
TW.start()
'''


T3 = add_DAGTX()
T3.start()

time.sleep(5)
#print("result ================ ",len(create_chain_from_dump(blockchain.chain)))
'''