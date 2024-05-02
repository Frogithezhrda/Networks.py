import requests

IP = "http://pizz4.cyber.org.il/userinfo/"
IP2 = "?no_cache=00310036002e0034002e0032003000320034002c002000310035003a00300038003a00350034"
PORT = 80
for num in range(1, 1050):
    req = requests.get(IP + str(num) + IP2)
    print(str(num) + ":" + req.text)
