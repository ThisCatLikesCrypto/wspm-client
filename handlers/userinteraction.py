import sys

RED = '\033[38;5;203m'
ORANGE = '\033[38;5;208m'
GREEN = '\033[38;5;120m'
YELLOW = '\033[38;5;226m'
BLUE = '\033[38;5;117m' #dark-aqua sort of colour
BLUE2 = '\033[96m' #darker blue

def producesyntaxed(text: str, color='\033[38;5;120m'):
    try:
        sys.stdout.write(color + text + '\033[0m')
    except:
        print(text)

def pront(stufftoprint, colour=BLUE):
    stufftoprint = str(stufftoprint) + "\n"
    producesyntaxed(stufftoprint, colour)