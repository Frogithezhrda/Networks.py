import socket
import chatlib
import random
import select

# GLOBALS
users = {"Omer": {"password": "Saban", "score": 10, "question_asked": [1]},
         "Harel": {"password": "Dorani", "score": 10, "question_asked": []}, }
questions = {1: ["How much 1+1?", "5", "6", "7", "2", "4"],
             2: ["Capital Of Israel?", "Tel Aviv", "Jerusalem", "Ashdod", "Arugot", "2"]}
logged_users = {}  # a dictionary of client hostnames to usernames - will be used later
messages_to_send = []

ERROR_MSG = "Error! "
SERVER_PORT = 5678
SERVER_IP = "127.0.0.1"


# HELPER SOCKET METHODS


def create_random_question():
    global questions
    random_number = random.randint(1, 2)
    question = str(random_number) + '#'
    question += '#'.join(questions[random_number])
    return question[:-2]


def handle_question_message(conn):
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["your_question"], create_random_question())


def handle_answer_message(conn, username, answer):
    global questions
    question_id, answer = chatlib.split_data(answer, 1)
    question_id = int(question_id)
    right_answer = questions[question_id][5]
    if int(right_answer) == int(answer):
        build_and_send_message(conn, chatlib.PROTOCOL_SERVER["correct"])
        score = int(users[username]["score"]) + 5
        users[username]["score"] = str(score)
    else:
        build_and_send_message(conn, chatlib.PROTOCOL_SERVER["wrong"], right_answer)

def build_and_send_message(conn, code, data=""):
    """
	Builds a new message using chatlib, wanted code and message.
	Prints debug info, then sends it to the given socket.
	Paramaters: conn (socket object), code (str), data (str)
	Returns: Nothing
	"""
    try:
        message = chatlib.build_message(code, data)
        print("[SERVER] ", conn.getpeername(), message)
        conn.sendall(message.encode())

        # Print debug information

    except Exception as exception:
        print(exception)


def recv_message_and_parse(conn):
    """
	Recieves a new message from given socket,
	then parses the message using chatlib.
	Paramaters: conn (socket object)
	Returns: cmd (str) and data (str) of the received message.
	If error occured, will return None, None
	"""
    try:
        full_msg = conn.recv(1024).decode()
        print("[CLIENT] ", conn.getpeername(), full_msg)
        cmd, data = chatlib.parse_message(full_msg)
        return cmd, data
    except Exception as exception:
        return None, None


# Data Loaders #
def load_questions():
    """
	Loads questions bank from file	## FILE SUPPORT TO BE ADDED LATER
	Recieves: -
	Returns: questions dictionary
	"""
    questions = {
        2313: {"question": "How much is 2+2", "answers": ["3", "4", "2", "1"], "correct": 2},
        4122: {"question": "What is the capital of France?", "answers": ["Lion", "Marseille", "Paris", "Montpellier"],
               "correct": 3}
    }

    return questions


def load_user_database():
    users = {
        "test": {"password": "test", "score": 0, "questions_asked": []},
        "yossi": {"password": "123", "score": 50, "questions_asked": []},
        "master": {"password": "master", "score": 200, "questions_asked": []}
    }
    return users


# SOCKET CREATOR

def setup_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (SERVER_IP, SERVER_PORT)
    sock.bind(server_address)
    sock.listen(1)
    return sock


def send_error(conn, error_msg):
    """"""
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["login_failed_msg"], ERROR_MSG + error_msg)


def handle_logged_message(conn):
    global logged_users
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["logged_answer"], '\n'.join(logged_users.values()))


def handle_highscore_message(conn):
    global users
    scores = ""
    for user in users:
        scores += f"{user}: {users[user]['score']} \n"
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["all_score"], scores[:-1])


def handle_getscore_message(conn, username):
    global users
    user_score = users[username]["score"]
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["score"], str(user_score))


def handle_logout_message(conn):
    """
	Closes the given socket (in laster chapters, also remove user from logged_users dictioary)
	Recieves: socket
	Returns: None
	"""
    global logged_users
    logged_users[conn.getpeername()] = ""
    print("Connection closed")
    conn.close()


# Implement code ...


def handle_login_message(conn, data):
    """
	Gets socket and message data of login message. Checks  user and pass exists and match.
	If not - sends error and finished. If all ok, sends OK message and adds user and address to logged_users
	Recieves: socket, message code and data
	Returns: None (sends answer to client)
	"""
    global users  # This is needed to access the same users dictionary from all functions
    global logged_users  # To be used later

    username, password = chatlib.split_data(data, 1)

    if username in users:
        if users[username]["password"] == password:
            build_and_send_message(conn, chatlib.PROTOCOL_SERVER["login_ok_msg"])
            logged_users[conn.getpeername()] = username
        else:
            send_error(conn, "Incorrect password")
    else:
        send_error(conn, "Username does not exist")


# Implement code ...

def print_client_sockets():
    global logged_users
    for user in logged_users:
        print(user)
def handle_client_message(conn, cmd, data):
    """
	Gets message code and data and calls the right function to handle command
	Recieves: socket, message code and data
	Returns: None
	"""
    global logged_users  # To be used later
    if cmd == chatlib.PROTOCOL_CLIENT["login_msg"]:
        handle_login_message(conn, data)
    elif cmd == chatlib.PROTOCOL_CLIENT["logout_msg"] or cmd == "":
        handle_logout_message(conn)
    elif cmd == chatlib.PROTOCOL_CLIENT["logout_msg"]:
        handle_logout_message(conn)
        # client_socket, client_address = conn.accept()
        # print(f"New Client joined! {client_address}")
    elif cmd == chatlib.PROTOCOL_CLIENT["my_score"]:
        handle_getscore_message(conn, str(logged_users[conn.getpeername()]))
    elif cmd == chatlib.PROTOCOL_CLIENT["highscore"]:
        handle_highscore_message(conn)
    elif cmd == chatlib.PROTOCOL_CLIENT["logged"]:
        handle_logged_message(conn)
    elif cmd == chatlib.PROTOCOL_CLIENT["play_question"]:
        handle_question_message(conn)
    elif cmd == chatlib.PROTOCOL_CLIENT["send_answer"]:
        handle_answer_message(conn, str(logged_users[conn.getpeername()]), data)
    else:
        send_error(conn, "Unknown Function!")


def main():
    global users
    global questions
    global messages_to_send
    global logged_users
    print("Welcome to Trivia Server!")

    connection = setup_socket()

    try:
        client_sockets_list = []

        while True:
            ready_to_read, ready_to_write, in_error = select.select([connection] + client_sockets_list, client_sockets_list, [])
            for current_socket in ready_to_read:
                if current_socket is connection:
                    (client_socket, client_address) = connection.accept()
                    print("\nNew Client joined!", client_address)
                    client_sockets_list.append(client_socket)
                    print_client_sockets()
                else:
                    cmd, data = recv_message_and_parse(current_socket)
                    if cmd == chatlib.PROTOCOL_CLIENT["login_msg"]:
                        if chatlib.split_data(data, 1)[0] not in logged_users.values():
                            handle_login_message(current_socket, data)
                        else:
                            send_error(current_socket, "Already Connected From Else Where!")
                    elif cmd == chatlib.PROTOCOL_CLIENT["logout_msg"]:
                        handle_logout_message(current_socket)
                        client_sockets_list.remove(current_socket)
                        # current_socket, client_address = connection.accept()
                        # print(f"New Client joined! {client_address}")
                    elif cmd == chatlib.PROTOCOL_CLIENT["my_score"]:
                        handle_getscore_message(current_socket, str(logged_users[current_socket.getpeername()]))
                    elif cmd == chatlib.PROTOCOL_CLIENT["highscore"]:
                        handle_highscore_message(current_socket)
                    elif cmd == chatlib.PROTOCOL_CLIENT["logged"]:
                        handle_logged_message(current_socket)
                    elif cmd == chatlib.PROTOCOL_CLIENT["play_question"]:
                        handle_question_message(current_socket)
                    elif cmd == chatlib.PROTOCOL_CLIENT["send_answer"]:
                        handle_answer_message(current_socket, str(logged_users[current_socket.getpeername()]), data)
                    elif cmd:
                        # handle_client_message(current_socket, cmd, data)
                        send_error(current_socket, "Not A Valid Command")
                    else:
                        handle_logout_message(current_socket)
                        client_sockets_list.remove(current_socket)
                        # client_socket, client_address = connection.accept()
                        # print(f"New Client joined! {client_address}")

    except KeyboardInterrupt:
        print("KeyboardInterrupt detected. Exiting gracefully...")
    except ConnectionResetError:
        print("Connection reset by client.")
    except Exception as e:
        print("Error:", e)
    finally:
        if current_socket:
            client_sockets_list.remove(current_socket)
        # client_socket, client_address = connection.accept()
        # print(f"New Client joined! {client_address}")


if __name__ == '__main__':
    main()
