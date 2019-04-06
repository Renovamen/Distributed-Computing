import xmlrpc.client
import threading
import time
import sys
import base64

class serverThread(threading.Thread):
    def __init__(self, serverID, address, filepath, pattern, result):
        threading.Thread.__init__(self)
        self.serverID = serverID
        self.address = address
        self.filepath = filepath
        self.pattern = pattern
        self.result = result

    def run(self):
        vmID = self.serverID - 1
        # XML-RPC连接各个服务端
        server = xmlrpc.client.ServerProxy('http://' + self.address + ':8080')

        # 服务端正在运行
        try:
            query = server.query(self.filepath, self.pattern)
            query_decoded = base64.b64decode(query.data).decode("utf-8")
            self.result[vmID] = query_decoded

        # 服务端挂了, 输出错误信息
        except Exception as exception:
            self.result[vmID] = str(self.serverID) + ': ' + self.address +' is shut down'
            print(self.result[vmID])
            print(exception)

# 对每个服务端都创建一个线程
def createThread(filepath, pattern):
    result = [None]*5
    serverAdd = []
    threads = []
    output = []
    test = filepath.split('.log')
    # 5个服务端
    for i in range(5):
        # 主机名
        # serverAdd.append('renovamen-' + str(i + 1).zfill(2) )
        # 192.168.225.200 - 192.168.225.204
        serverAdd.append('192.168.225.2' + str(i).zfill(2) )
        output.append(test[0]+str(i + 1)+'.log')
    for i, address in enumerate(serverAdd):
        threads.append(serverThread(i + 1, address, output[i], pattern, result))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return result

if __name__ == '__main__':
    start = time.time()
    total = 0
    lines = []

    # sys.argv[]: 获取命令行参数(外部
    # 有输入
    if len(sys.argv) > 1:
        print("Log file:" + sys.argv[1] + "pattern:" + sys.argv[2])
        filepath = sys.argv[1]
        pattern = sys.argv[2]
        result = createThread(filepath, pattern)
    # 无输入, 用默认log路径和查询内容
    else:
        print('Regular')
        filepath = 'machine.log'
        pattern = 'ZouXiaohanissocool'
        result = createThread(filepath, pattern)
    end = time.time()

    # 每个服务端的返回结果
    for i, s in enumerate(result):
        serverRe = result[i].splitlines()
        lines.append(len(serverRe))
        total = total + len(serverRe)
        # 路径不存在或该服务端未工作
        if (len(serverRe) == 1 and ('No such file or directory' in serverRe[0] or 'is shut down' in serverRe[0])):
            total = total - 1
            lines[i] = 0

    # 每个服务端的输出
    for i, num in enumerate(lines):
        ID = i+1
        print("VM No.",ID,"matches",num,"lines.")
    print("Total found:",total,"lines.")
    print("Total time:",(end - start),"seconds.")
