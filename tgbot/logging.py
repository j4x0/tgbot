from colorama import Fore, Style
import time

def log(text, error = False, info = False):
    color = ""
    symbol = "#"
    if error:
        color = Fore.RED
        symbol = "!"
    elif info:
        color = Fore.YELLOW
        symbol = "~"
    print(color + "{0} [{1}] {2}".format(time.strftime("%H:%M:%S"), symbol, text) + Style.RESET_ALL)

def info(text):
    return log(text, info = True)

def error(text):
    return log(text, error = True)
