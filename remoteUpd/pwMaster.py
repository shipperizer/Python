import sys

def getPW(macAddr):
    mac=macAddr
    mac=mac.rsplit(":")
    a=[]
    for i in range(len(mac)):
        a.append(ord(mac[i][-1])+3*i)
        a.append(ord(mac[i][-2])+5*i)
    a.sort(reverse=True)
    mac = ""
    for i in range(len(a)):
        mac = mac + chr(a[i])
    return mac
        

