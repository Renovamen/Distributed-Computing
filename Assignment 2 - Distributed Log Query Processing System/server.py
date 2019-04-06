from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import subprocess
import base64

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# 服务端ip
server = SimpleXMLRPCServer(('192.168.225.200', 8080), requestHandler=RequestHandler)
# server = SimpleXMLRPCServer(('192.168.225.201', 8080), requestHandler=RequestHandler)
# server = SimpleXMLRPCServer(('192.168.225.202', 8080), requestHandler=RequestHandler)
# server = SimpleXMLRPCServer(('192.168.225.203', 8080), requestHandler=RequestHandler)
# server = SimpleXMLRPCServer(('192.168.225.204', 8080), requestHandler=RequestHandler)
server.register_introspection_functions()

# 日志查询
def query(file, parttern):
    cmd = 'cat ' + file + ' | grep ' + parttern
    res = subprocess.run(cmd, stdout = subprocess.PIPE, shell = True, encoding = 'utf-8')
    # base64: 解码xmlRPC中的数据
    result = base64.b64encode(res.stdout.encode('utf-8'))
    return result
server.register_function(query,'query')

# 永久运行服务端
server.serve_forever()