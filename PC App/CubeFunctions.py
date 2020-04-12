from time import sleep
from keyboard import Keyboard
import logging

logger = logging.getLogger("Logger")

def arrow_key(value, AfterDelay=1.0):
    if value < 0:
        Keyboard.key(Keyboard.VK_RIGHT)
    elif value > 0:
        Keyboard.key(Keyboard.VK_LEFT)
    sleep(AfterDelay)


def change_volume(iterator, threshold, AfterDelay):
    result = iterator(threshold)
    while result is not False:
        result = iterator(threshold)
        if result < 0:
            Keyboard.key(Keyboard.VK_VOLUME_DOWN)
        elif result > 0:
            Keyboard.key(Keyboard.VK_VOLUME_UP)

    #sleep(AfterDelay)


def change_song(iterator, threshold, AfterDelay):
    result = iterator(threshold)
    while result is not False:
        result = iterator(threshold)
        if result < 0:
            Keyboard.key(Keyboard.VK_MEDIA_PREV_TRACK)
        elif result > 0:
            Keyboard.key(Keyboard.VK_MEDIA_NEXT_TRACK)
        #sleep(AfterDelay)


def change_desktop(iterator, threshold, AfterDelay):
    result = iterator(threshold)
    while result is not False:
        result = iterator(threshold)

        Keyboard.keyDown(Keyboard.VK_CONTROL)
        Keyboard.keyDown(Keyboard.VK_LWIN)
        arrow_key(-result, AfterDelay=0.01)
        Keyboard.keyUp(Keyboard.VK_LWIN)
        Keyboard.keyUp(Keyboard.VK_CONTROL)
        logging.warning(f"Changed Desktop")
    #sleep(AfterDelay)


def change_window(iterator, threshold, AfterDelay):
    Keyboard.keyDown(Keyboard.VK_ALT)
    Keyboard.key(Keyboard.VK_TAB)

    result = iterator(threshold)
    while result is not False:
        result = iterator(threshold)
        arrow_key(result, AfterDelay=0.01)

    Keyboard.keyUp(Keyboard.VK_ALT)

    #sleep(AfterDelay)