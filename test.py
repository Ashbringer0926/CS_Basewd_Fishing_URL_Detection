import socket

client = socket.socket()
client.connect(('120.76.134.91', 9001))
while True:

    info = input('>>>')                     #输入数据，编码并发送给服务端
    info = info.encode('gbk')
    client.send(info)

    s_info = client.recv(1024)  # 接受服务端的消息并解码
    s_info = s_info.decode(encoding='gbk')
    print(s_info)
    print(type(s_info))
    if s_info == 'bye':  # 如果服务端发送的消息为bye，回复bye，结束循环
        client.send(b'bye')
        print('bye_1')
        break
client.close()