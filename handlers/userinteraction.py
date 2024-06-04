import sys

BLUE = '\033[38;5;117m'
GREEN = '\033[38;5;120m'
RED = '\033[38;5;203m'

def producesyntaxed(text: str, color='\033[38;5;120m'):
    try:
        sys.stdout.write(color + text + '\033[0m')
    except:
        print(text)

def pront(stufftoprint, colour=BLUE):
    stufftoprint = str(stufftoprint) + "\n"
    producesyntaxed(stufftoprint, colour)