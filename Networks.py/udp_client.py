import socket
IP = "127.0.0.1"
PORT = 8821
MAX_MSG_SIZE = 1024

my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    message = input("To The Server: ")
    my_socket.sendto(message.encode(), (IP, PORT))
    (response, remote_address) = my_socket.recvfrom(MAX_MSG_SIZE)
    data = response.decode()
    print(data)
    if message == "EXIT":
        break
my_socket.close()

