import socket
import chatlib
import sys

SERVER_IP = "127.0.0.1"  # Our server will run on same computer as client
SERVER_PORT = 5678


# HELPER SOCKET METHODS

def get_score(conn):
    msg_code, data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["my_score"])
    return data


def get_highscore(conn):
    cmd, data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["highscore"])
    print(data)

def get_logged_users(conn):
    cmd, data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["logged"])
    print(data)

def play_question(conn):
    cmd, data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["play_question"])
    answers = data.split('#')
    question_id = ''.join(answers[:1])
    questions = '\n'.join(data.split('#')[1:2])
    print(f"Q: {questions}: ")
    for answer_index in range(len(data.split('#')[2:])):
        print(f"\t\t{answer_index + 1}. {''.join(answers[2 + answer_index:answer_index + 3])}")
    answer = input("Please choose an answer [1-4]: ")
    cmd, data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["send_answer"], question_id + '#' + answer)
    if "CORRECT_ANSWER" in cmd:
        print("Correct!")
    else:
        print("Wrong! The Right Answer is #" + data)


def build_and_send_message(conn, code, data=""):
    """
	Builds a new message using chatlib, wanted code and message.
	Prints debug info, then sends it to the given socket.
	Paramaters: conn (socket object), code (str), data (str)
	Returns: Nothing
	"""
    try:
        # Build the message using chatlib's build_message function
        message = chatlib.build_message(code, data)
        # Send the message to the server through the socket
        conn.sendall(message.encode())

        # Print debug information

    except Exception as exception:
        error_and_exit(exception)


def recv_message_and_parse(conn):
    """
	Recieves a new message from given socket,
	then parses the message using chatlib.
	Paramaters: conn (socket object)
	Returns: cmd (str) and data (str) of the received message.
	If error occured, will return None, None
	"""
    # Implement Code
    # ..
    try:

        full_msg = conn.recv(1024).decode()

        # Parse the received message using chatlib
        cmd, data = chatlib.parse_message(full_msg)

        # Return the command and data extracted from the message
        return cmd, data
    except Exception as exception:
        print(exception)
        return None, None


def connect():
    # Implement Code
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (SERVER_IP, SERVER_PORT)
    sock.connect(server_address)
    return sock


def error_and_exit(error_msg):
    print("Error:" + str(error_msg))
    sys.exit(1)


def build_send_recv_parse(conn, cmd, data=""):
    build_and_send_message(conn, cmd, data)
    return recv_message_and_parse(conn)


def login(conn):
    username = input("Please enter username: \n")
    password = input("Please enter password: \n")
    # Implement code
    try:
        build_and_send_message(conn, chatlib.PROTOCOL_CLIENT["login_msg"], username + '#' + password)
    except Exception as exception:
        error_and_exit(exception)


def logout(conn):
    # Implement code
    build_and_send_message(conn, chatlib.PROTOCOL_CLIENT["logout_msg"])
    conn.close()


def choices(connection):
    while True:
        print("s\tGet my score\nh\tGet high score\np\tPlay trivia question\nl\tGet logged users\nq\tQuit")
        choice = input("Please enter your choice: ")
        if choice == 's':
            print("Your Score:", get_score(connection))
        elif choice == 'h':
            get_highscore(connection)
        elif choice == 'p':
            play_question(connection)
        elif choice == 'l':
            get_logged_users(connection)
        elif choice == 'q':
            print("Goodbye!")
            logout(connection)
            break


def main():
    connection = connect()
    login(connection)
    try:
        while True:
            cmd, data = recv_message_and_parse(connection)
            if "ERROR" in cmd:
                print("Error:", data)
                login(connection)
            elif "LOGIN_OK" in cmd:
                print("Logged in!")
                choices(connection)
                break
    except Exception as e:
        error_and_exit(e)


if __name__ == '__main__':
    main()
