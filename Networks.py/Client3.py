import socket


# Function to handle disconnection
def on_disconnect():
    print("Client disconnected from the server.")


# Connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 5555))
print("Successfully connected to the server!")

try:
    while True:
        # Add any additional actions here if you want to receive data from the server
        pass

except KeyboardInterrupt:  # Triggered when the user presses Ctrl+C
    print("Client disconnected.")
    client_socket.close()  # Close the connection with the server
except ConnectionResetError:  # Handle disconnection from the server
    on_disconnect()
