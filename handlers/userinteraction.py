import sys

BLUE = '\033[38;5;117m'

def producesyntaxed(text, color='\033[38;5;120m'):
    try:
        sys.stdout.write(color + text + '\033[0m')
    except:
        print(text)

def pront(stufftoprint, colour=BLUE):
    stufftoprint = str(stufftoprint) + "\n"
    if __name__ == "__main__":
        producesyntaxed(stufftoprint, colour)
    else:
        producesyntaxed(f"{__name__}: {stufftoprint}", BLUE)