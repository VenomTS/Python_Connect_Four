import time

import pyautogui

from board import Board

ROWS = 6
COLS = 7

def gameOn(x, y):
    board = Board(ROWS, COLS, x, y)
    board.calculatePosition()
    while not board.gameEnded()[0]:
        board.updateBoard()
        if board.move:
            board.makeMove()
            time.sleep(1)

def main():
    input()
    x, y = pyautogui.position()
    pyautogui.moveTo(50, 50)
    time.sleep(1)
    gameOn(x, y)

main()



