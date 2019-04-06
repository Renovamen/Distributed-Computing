# Distributed Log Query Processing

## Design

语言：Python

用 4 台机器作为服务端，1 台机器作为客户端，基于TCP服务，客户端和服务端之间使用XML-RPC进行通信。



### Client

客户端 `client.py` 会为每一个服务端建立一个单独的线程来实现并行。从客户端输入查询命令（参数包括日志路径和查询内容），然后客户端将查询发送到每个服务端。 服务端会监听和处理查询请求，然后将查询结果返回给客户端。 最后，客户端会显示所有服务端的查询结果，包括匹配到的行和总行数。

```python
# 客户端XML-RPC
server = xmlrpc.client.ServerProxy('http://' + {{服务端ip}} + ':8080')
```



### Server

服务端 `server.py` 收到客户端发来的请求后，会使用grep查询日志，然后把结果返回给客户端。

```python
# 服务端XML-RPC
server = SimpleXMLRPCServer(({{本机ip}}, 8080), requestHandler=RequestHandler)
server.register_introspection_functions()
```





## Unit Test

测试过程为：现在每个服务端本地生成日志，然后在客户端分别查询频繁 / 一般 / 很少 出现的内容。



### Generate Log

`logfile.py` 将在每个服务端本地生成 machinei.log 文件（i 为机器编号），里面包含了频繁 / 一般 / 很少 出现的内容，为后面的测试做准备。



### Test

`unit_test.py` 会在每个服务端查询频繁 / 一般 / 很少 出现的内容，然后判断实验结果和预期是否相符。

P.S 也可以使用样例测试





## Usage

### Server

```python
python server.py # 服务端
```



### Client

```python
python client.py logpath pattern # 自定日志路径和查询内容 
python client.py # 默认⽇志路径和查询内容
```



### Log

```python
python logfile.py i # 生成日志 i为节点编号
```



### Unit Test

```python
python test.py # 单元测试
```