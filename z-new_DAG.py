from hashlib import sha256
import json
import time
import threading 
from threading import Lock,Thread
import random
import multiprocessing


tips = []


time1 = 0
time2 = 0

dict_ = {'0':"0000" ,'1':"0001" ,'2':"0010" ,'3':"0011" ,'4':"0100" ,'5':"0101" ,'6':"0110",'7':"0111",'8':"1000",'9':"1001",'a':"1010",'b':"1011",'c':"1100",'d':'1101','e':"1110",'f':"1111"}

class Vertex:
    def __init__(self,hash_,pre1,pre2,flag,weight,accumulate,time):
        self.hash_ = hash_
        self.pre1 = pre1
        self.pre2 = pre2
        self.flag = flag
        self.next = []
        self.weight = weight
        self.accumulate = accumulate
        self.time = time

mine_block1 = [Vertex("genesis","pre","pre",True,1,0,time.time())]
mine_block2 = [Vertex("genesis","pre","pre",True,1,0,time.time())]

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash , author,nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.author = author
        self.nonce = nonce
        

def compute_hash(block):
    block_string = json.dumps(block.__dict__, sort_keys=True)
    tmp_hash = sha256(block_string.encode()).hexdigest()
    result = ''
    for i in tmp_hash:
        result += dict_[i]
    return result

def proof_of_work(block,tmp_index,index,difficulty):
    block.nonce = 0
    computed_hash = compute_hash(block)
    difficulty_ = difficulty.value
    while not computed_hash.startswith('0' * difficulty_):
        block.nonce += 1
        if block.nonce % 1000 == 0:
            if tmp_index < index.value:
                return False
        computed_hash = compute_hash(block)
    print(index.value)
    return computed_hash

def package(port):
    transaction = []
    for i in port:
        tx_data = "{u'content': u'"+i.hash_+ "', 'timestamp': "+str(i.time)+", u'author': u'test_node',u'pre1':u'"+str(i.pre1)+"',u'pre2':u'"+str(i.pre2)+"',u'next':'"+str(i.next)+"'}"
        tx_ = eval(tx_data)
        transaction.append(tx_)
    return transaction

def mine(author,index,DAG_blockchain,difficulty):
    tmp_index = index.value
    timestamp_ = time.time()
    new_block = Block(index=tmp_index + 1,
                        transactions=[ ],
                        timestamp=timestamp_,
                        author = author,
                        previous_hash="hash")
    proof = proof_of_work(new_block,tmp_index,index,difficulty)

    if proof == False:
        return False     
    new_block.hash = proof 
    DAG_blockchain.put(new_block)
    index.value += 1

    return True

def mine_(author,index,DAG_blockchain,difficulty):
    while True:
        mine(author,index,DAG_blockchain,difficulty)


class change_difficult(threading.Thread):
    def __init__(self):
        super(change_difficult,self).__init__() 
    def run(self):
        global DAG_blockchain
        global difficulty
        
        tmp_index = index.value
        btime = DAG_blockchain.get().timestamp
        time_list.append(btime)
        while True:
            if index.value != tmp_index:
                sum_time = 0
                time_list.append(DAG_blockchain.get().timestamp)
                for i in range(1,len(time_list)):
                    sum_time += time_list[i] - time_list[i-1]
                if sum_time / len(time_list) < 15:
                    if difficulty.value < 25:
                        difficulty.value += 1
                else:
                    if difficulty.value > 20:
                        difficulty.value -= 1
                f = open("z-average-time.txt",mode="a")
                f.write(str(sum_time / len(time_list)))
                f.write("\r\n")
                f.close()
                f = open("z-time_interval.txt",mode="a")
                t = time_list[-1] - time_list[len(time_list) - 2]
                f.write("%f \r\n"%t)
                f.close()


def chose_tips():
    global tips
    tips_lock.acquire()
    if len(tips) == 1:
        pre1 = tips[0]
        pre2 = tips[0]
    else:
        a = random.randint(0, len(tips) - 1)
        b = random.randint(0, len(tips) - 1)
        while a == b:
            b = random.randint(0, len(tips) - 1)
        pre1 = tips[a]
        pre2 = tips[b]
    tips_lock.release()
    return pre1, pre2


def add_tx(pre1,pre2):
    global tips #在这里加个判断，要是出了新区块，就放弃这次添加交易
    tips_lock.acquire()
    new_tx = Vertex("content",pre1,pre2,True,1,0,time.time())
    pre1.next.append(new_tx)
    pre2.next.append(new_tx)
    if pre1 in tips:
        tips.remove(pre1)
    if pre2 in tips:
        tips.remove(pre2)
    tips.append(new_tx)#这里的问题！！！ 旧的交易连接上一个区块的节点，加入了下一个区块的池子
    tips_lock.release()
    
class add_DAGTX(threading.Thread):
    def __init__(self,n):
        super(add_DAGTX,self).__init__()
        self.n = n
    def run(self):
        while True:
            pre1,pre2 = chose_tips()
            t = random.uniform(0,2)
            time.sleep(t)
            add_tx(pre1,pre2)
            t = random.uniform(0,1)
            time.sleep(t)

def statistics(genesis):
    time_now = time.time()
    list1 = [genesis]
    list2 = []
    result = [1]
    layer_num = 0
    num = 0
    notresult = [genesis]
    statistics = [genesis]
    while list1 or list2 :
        layer_num += 1
        for i in list1:
            for j in i.next:
                if j not in list2 and j not in notresult:
                    list2.append(j)
                    notresult.append(j)
                    num += 1
        result.append(num)
        for i in list2:
            statistics.append(i)
        list1 = []
        num = 0
        if list2:
            for i in list2:
                for j in i.next:
                    if j not in list1 and j not in notresult:
                        list1.append(j)
                        notresult.append(j)
                        num += 1
            result.append(num)
        for i in list1:
            statistics.append(i)
        list2 = []
        num = 0  
    f= open("z-timedata.txt",mode="a")
    f.write("block time :{} \r\n".format(str(time_now)))
    for i in statistics:
        f.write("%f \r\n"%i.time)
    f.close()
    print(result)
    return result

    

class connection(threading.Thread):
    def __init__(self,index):
        super(connection,self).__init__()
        self.index = index
    def run(self):
        global tips
        genesis_tx = Vertex("genesis","pre","pre",False,1,0,time.time())
        length = self.index.value
        blockchain_genesis = Vertex("genesis0",genesis_tx,genesis_tx,False,1,0,time.time())
        while True:
            time.sleep(0.1)
            if length != self.index.value:
                print("input--------------------------------------------")
                length = self.index.value
                tips_lock.acquire()
                tips = []
                genesis_tx = Vertex("genesis"+str(length),genesis_tx,genesis_tx,False,1,0,time.time())
                tips.append(genesis_tx)
                tips_lock.release()
                
                # t = shape_log(blockchain_genesis)
                # t.start()

                P = multiprocessing.Process(target=run_process,args=(blockchain_genesis,))
                P.start()

                #statistics(blockchain_genesis)
                blockchain_genesis = genesis_tx


'''
class shape_log(threading.Thread):
    def __init__(self,genesis):
        super(shape_log,self).__init__()
        self.genesis = genesis
    def run(self):
        all_transactions = []
        all_transactions.append(self.genesis)
        for i in all_transactions:
            for j in i.next:
                if j not in all_transactions:
                    all_transactions.append(j)
        all_transactions.pop(0)
        average_ = []
        for i in all_transactions:
            tmp_stack1 = []
            time1 = []
            if i.pre1.flag == True:
                tmp_stack1.append(i.pre1)
                time1.append(i.pre1.time)
            if i.pre2.flag == True:
                tmp_stack1.append(i.pre2)
                time1.append(i.pre2.time)
            for j in tmp_stack1:
                if j.pre1.flag == True:
                    if j.pre1.time not in time1:
                        tmp_stack1.append(j.pre1)
                        time1.append(j.pre1.time)
            for j in tmp_stack1:
                if j.pre2.flag == True:
                    if j.pre2.time not in time1:
                        tmp_stack1.append(j.pre2)
                        time1.append(j.pre2.time)
            print("all",len(all_transactions),"pre",len(tmp_stack1)) 
            tmp_stack2 = []
            time2 = [] 
            for k in i.next:
                tmp_stack2.append(k)
                time2.append(k.time)           
            for n in tmp_stack2:
                if n.time not in time2:
                    tmp_stack2.append(n)
                    time2.append(n.time)
            print("next",len(tmp_stack2))            
'''
class shape_log(threading.Thread):
    def __init__(self,genesis):
        super(shape_log,self).__init__()
        self.genesis = genesis
    def run(self):
        print("threading run !!!!!")
        all_transactions = []
        all_transactions.append(self.genesis)
        tips_lock.acquire()
        for i in all_transactions:

            for j in i.next:
                if j not in all_transactions:
                    all_transactions.append(j)
        tips_lock.release()
        all_transactions.pop(0)
        average_ = []
        print("all = ",len(all_transactions))
        for i in all_transactions:
            num = 0
            tmp_stack = []
            pre1 = i.pre1
            pre2 = i.pre2
            if pre1.flag == True:
                if pre1 in all_transactions:
                    tmp_stack.append(pre1)
            if pre2.flag == True:
                if pre2 in all_transactions:
                    tmp_stack.append(pre2)
            for j in tmp_stack:
                if j.pre1.flag == True :
                    if j.pre1 not in tmp_stack:
                        if j.pre1  in all_transactions:
                            tmp_stack.append(j.pre1)
                if j.pre2.flag == True :
                    if j.pre2 not in tmp_stack:
                        if j.pre2  in all_transactions:
                            tmp_stack.append(j.pre2) 
            tmp_stack2 = []
            for k in i.next:
                tmp_stack2.append(k)
            for n in tmp_stack2:
                for m in n.next:
                    if m not in tmp_stack:
                        if m  in all_transactions:
                            tmp_stack2.append(m)
            #print("tmp_stack2",len(tmp_stack2))
            average_.append(len(tmp_stack)+len(tmp_stack2))
        block_index = self.genesis.hash_[7:]
        average_len = 0
        for tx in average_:
            average_len += tx
        if len(all_transactions) != 0:
            average_len = average_len/len(all_transactions)

        shape = statistics(self.genesis)

        content = {"index":block_index,"average":str(average_len),"transaction":len(all_transactions),"shape":str(shape)}
        f= open("z-shape.json",mode="a")
        json.dump(content,f)
        f.write("\r\n")
        f.close()
        # print("len",len(all_transactions))
        print("end")                

def run_process(genesis):
    print("threading run !!!!!")
    all_transactions = []
    all_transactions.append(genesis)
    tips_lock.acquire()
    for i in all_transactions:
        for j in i.next:
            if j not in all_transactions:
                all_transactions.append(j)
    tips_lock.release()
    all_transactions.pop(0)
    average_ = []

    for i in all_transactions:
        tmp_stack = []
        pre1 = i.pre1
        pre2 = i.pre2

        if pre1.flag == True:
            if pre1 in all_transactions:
                tmp_stack.append(pre1)
        if pre2.flag == True:
            if pre2 in all_transactions:
                tmp_stack.append(pre2)
        for j in tmp_stack:
            if j.pre1.flag == True :
                if j.pre1 not in tmp_stack:
                    if j.pre1  in all_transactions:
                        tmp_stack.append(j.pre1)
            if j.pre2.flag == True :
                if j.pre2 not in tmp_stack:
                    if j.pre2  in all_transactions:
                        tmp_stack.append(j.pre2) 
        tmp_stack2 = []
        for k in i.next:
            tmp_stack2.append(k)
        for n in tmp_stack2:
            for m in n.next:
                if m not in tmp_stack2:
                    if m  in all_transactions:
                        tmp_stack2.append(m)
        #print("tmp_stack2",len(tmp_stack2))
        average_.append(len(tmp_stack)+len(tmp_stack2))
    block_index = genesis.hash_[7:]
    average_len = 0
    for tx in average_:
        average_len += tx
    if len(all_transactions) != 0:
        average_len = average_len/len(all_transactions)

    shape = statistics(genesis)

    content = {"index":block_index,"average":str(average_len),"transaction":len(all_transactions),"shape":str(shape)}
    f= open("z-shape.json",mode="a")
    json.dump(content,f)
    f.write("\r\n")
    f.close()
    # print("len",len(all_transactions))
    print("end")


if __name__ == "__main__":
    tips_lock = threading.Lock()
    time_list = []
    DAG_blockchain = multiprocessing.Queue()
    index = multiprocessing.Value("i",0)
    difficulty = multiprocessing.Value("i",20)
    genesis_block0 = Block(0, [], time.time(), "genesis","0")
    DAG_blockchain.put(genesis_block0)
    t = change_difficult()
    t.start()
    for i in range(10):
        P = multiprocessing.Process(target=mine_,args=(i,index,DAG_blockchain,difficulty))
        P.start()
        print("process ",i)
    
    #add tx
    blockchain = []
    genesis_tx = Vertex("genesis","pre","pre",False,1,0,time.time())
    blockchain_genesis = genesis_tx
    tips.append(genesis_tx)
    # blockchain.append(Vertex("genesis","pre","pre",True,1,0,time.time()))
    for i in range(30):
        t = add_DAGTX(i)
        t.start()
    
    t1 = connection(index)
    t1.start()

    # while True:
    #     time.sleep(10)
    #     tips_lock.acquire()
    #     #print(statistics())
    #     tips_lock.release()

'''
DAG_blockchain = multiprocessing.Queue()
index = multiprocessing.Value("i",0)
tips_lock = threading.Lock()
tips = []
genesis_block0 = Block(0, [], time.time(), "genesis","0")
DAG_blockchain.put(genesis_block0)
genesis_tx = Vertex("genesis","pre","pre",False,1,0,time.time())
blockchain_genesis = genesis_tx
tips.append(genesis_tx)

for i in range(30):
    t = add_DAGTX(i)
    t.start()
print("hello")
time.sleep(60)
run_process(genesis_tx)
    
'''    
