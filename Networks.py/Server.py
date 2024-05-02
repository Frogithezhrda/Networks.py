import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 10095)
sock.bind(server_address)
sock.listen(1)
connection, client_address = sock.accept()

data = connection.recv(1024).decode()
data = data + "!!!"
data = data.upper()
connection.sendall(data.encode())
