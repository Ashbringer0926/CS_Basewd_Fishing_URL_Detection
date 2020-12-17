from sklearn.externals import joblib
import pandas as pd
import tldextract
import math
from urllib.parse import urlparse
import socket
import threading

Suspicious_TLD=['zip','cricket','link','work','party','gq','kim','country','science','tk']
Suspicious_Domain=['luckytime.co.kr','mattfoll.eu.interia.pl','trafficholder.com','dl.baixaki.com.br','bembed.redtube.comr','tags.expo9.exponential.com','deepspacer.com','funad.co.kr','trafficconverter.biz']

featureSet = pd.DataFrame(columns=('domain','entropy','num of hyphen','num of delim','len of domain','num of at',\
'is IP','presence of Suspicious_TLD','presence of suspicious domain','label'))


def countdots(url):
    return url.count('.')


def countdelim(url):
    count = 0
    delim = [';', '_', '?', '=', '&']
    for each in url:
        if each in delim:
            count = count + 1

    return count


import ipaddress as ip  # works only in python 3


def isip(uri):
    try:
        if ip.ip_address(uri):
            return 1
    except:
        return 0


def isPresentHyphen(url):
    return url.count('-')


def isPresentAt(url):
    return url.count('@')


def get_Ent(domain):
    # domain = get_Name(domain)
    tmp_dict = {}
    domain_len = len(domain)
    for i in range(0, domain_len):
        if domain[i] in tmp_dict.keys():
            tmp_dict[domain[i]] = tmp_dict[domain[i]] + 1
        else:
            tmp_dict[domain[i]] = 1
    shannon = 0
    for i in tmp_dict.keys():
        p = float(tmp_dict[i]) / domain_len
        shannon = shannon - p * math.log(p, 2)
    return shannon


def getFeatures(url, label):
    result = []
    url = str(url)

    path = urlparse(url)
    ext = tldextract.extract(url)
    domain = ext.domain
    # add the domain to feature set
    result.append(domain)

    result.append(get_Ent(domain))

    # checking hyphen in domain
    result.append(isPresentHyphen(domain))

    result.append(countdelim(domain))
    # length of domain
    result.append(len(domain))

    # checking @ in the url
    result.append(isPresentAt(domain))

    # if IP address is being used as a URL
    result.append(isip(domain))

    # presence of Suspicious_TLD
    result.append(1 if ext.suffix in Suspicious_TLD else 0)

    # presence of suspicious domain
    result.append(1 if '.'.join(ext[1:]) in Suspicious_Domain else 0)

    # result.append(get_ext(path.path))
    result.append(str(label))
    return result

    # Yay! finally done!


def main(message):

    result = pd.DataFrame(columns=('domain','entropy','num of hyphen','num of delim','len of domain','num of at',\
    'is IP','presence of Suspicious_TLD','presence of suspicious domain','label'))

    results = getFeatures(message, '1')
    result.loc[0] = results
    result = result.drop(['domain', 'label'], axis=1).values

    # print(clf.predict(result))
    return clf.predict(result)


def recv_msg(new_conn, new_addr):
    while True:
        try:
            c_info = new_conn.recv(1024).decode('gbk')  # 接受客户端消息并解码
            print("receive info from ", new_addr)
            info = main(c_info)
            info_send = str(info[0])
            info_send = info_send.encode('gbk')
            new_conn.send(info_send)
            if c_info == 'bye':  # 当客户端发送bye时，服务端给客户端发送bye并结束循环
                conn.send(b'bye')
                break
        except ConnectionResetError as e:
            print(e)
            break
    new_conn.close()


if __name__ == '__main__':
    clf = joblib.load('rfc.pkl')
    message = ''
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', 9001))

    server.listen()

    while True:
        conn, addr = server.accept()
        print('新用户[%s]连接' % str(addr))
        thread_msg = threading.Thread(target=recv_msg, args=(conn, addr))
        thread_msg.setDaemon(True)
        thread_msg.start()

    server.close()
