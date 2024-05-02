# Protocol Constants

CMD_FIELD_LENGTH = 16  # Exact length of cmd field (in bytes)
LENGTH_FIELD_LENGTH = 4  # Exact length of length field (in bytes)
MAX_DATA_LENGTH = 10 ** LENGTH_FIELD_LENGTH - 1  # Max size of data field according to protocol
MSG_HEADER_LENGTH = CMD_FIELD_LENGTH + 1 + LENGTH_FIELD_LENGTH + 1  # Exact size of header (CMD+LENGTH fields)
MAX_MSG_LENGTH = MSG_HEADER_LENGTH + MAX_DATA_LENGTH  # Max size of total message
DELIMITER = "|"  # Delimiter character in protocol
DATA_DELIMITER = "#"  # Delimiter in the data part of the message

# Protocol Messages 
# In this dictionary we will have all the client and server command names

PROTOCOL_CLIENT = {
    "login_msg": "LOGIN",
    "logout_msg": "LOGOUT",
    "my_score": "MY_SCORE",
    "highscore": "HIGHSCORE",
    "play_question": "GET_QUESTION",
    "send_answer": "SEND_ANSWER",
    "logged": "LOGGED"
}  # .. Add more commands if needed

PROTOCOL_SERVER = {
    "login_ok_msg": "LOGIN_OK",
    "login_failed_msg": "ERROR",
    "your_question": "YOUR_QUESTION",
    "score": "YOUR_SCORE",
    "all_score": "ALL_SCORE",
    "correct": "CORRECT_ANSWER",
    "wrong": "WRONG_ANSWER",
    "logged_answer": "LOGGED_ANSWER"
}  # ..  Add more commands if needed

# Other constants

ERROR_RETURN = None  # What is returned in case of an error


def build_message(cmd, data):
    """
    Gets command name (str) and data field (str) and creates a valid protocol message
    Returns: str, or None if an error occurred
    """
    if cmd is None or data is None:
        return None, None
    if cmd in ["LOGIN", "ALL_SCORE", "WRONG_ANSWER", "CORRECT_ANSWER",  "LOGGED_ANSWER", "MY_SCORE", "YOUR_QUESTION", "HIGHSCORE", "LOGOUT", "GET_QUESTION", "SEND_ANSWER", "LOGGED", "ERROR", "LOGIN_OK", "YOUR_SCORE"]:
        data_length = len(data)
        cmd_length = len(cmd)
        message_data = f"{cmd}" + ' ' * (CMD_FIELD_LENGTH - cmd_length) + f"|{data_length:04d}|{data}"  # Using f-string for string formatting
    else:
        return None
    return message_data


def parse_message(data):
    """
    Parses protocol message and returns command name and data field
    Returns: cmd (str), data (str). If some error occurred, returns None, None
    """
    counter = 0
    for data_block in data:
        if data_block == DELIMITER:
            counter += 1
    if counter < 2:
        return None, None
    data_splited = data.split(DELIMITER)
    data_splited[0] = data_splited[0].strip()
    try:
        if int(data_splited[1].strip()) == len(data_splited[2]):
            return data_splited[0], data_splited[2]
        else:
            return None, None
    except Exception as e:
        return None, None

def split_data(msg, expected_fields):
    """
	Helper method. gets a string and number of expected fields in it. Splits the string 
	using protocol's data field delimiter (|#) and validates that there are correct number of fields.
	Returns: list of fields if all ok. If some error occured, returns None
	"""
    counter = 0
    for letter in msg:
        if letter == DATA_DELIMITER:
            counter += 1
    if counter == expected_fields:
        msg_list = msg.split(DATA_DELIMITER)
        return msg_list


def join_data(msg_fields):
    """
    Helper method. Gets a list, joins all of its fields to one string divided by the data delimiter.
    Returns: string that looks like cell1#cell2#cell3
    """
    msg_fields = DATA_DELIMITER.join(msg_fields)
    return msg_fields
