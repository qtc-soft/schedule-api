import string
import random


# generate unique key
def keygen (size=12, chars=string.ascii_uppercase + string.digits) -> str:
    """
    :param size:
    :param chars:
    :return: String with unique key
    """
    return ''.join(random.choice(chars) for _ in range(size))