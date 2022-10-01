import time

import pyautogui

from board import Board

ROWS = 6
COLS = 7

def gameOn(x, y):
    board = Board(ROWS, COLS, x, y)
    while not board.gameEnded():
        board.updateBoard()
        if board.move:
            board.makeMove()
            time.sleep(3)

def main():
    input()
    x, y = pyautogui.position()
    pyautogui.moveTo(50, 50)
    gameOn(x, y)
main()



