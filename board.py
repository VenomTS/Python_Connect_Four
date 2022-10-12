import math

from PIL import ImageGrab

import pyautogui

class Spot:
    def __init__(self, row, col, color, startX, startY, distance):
        self.row = row
        self.col = col
        self.posX = (col * distance) + startX
        self.posY = (row * distance) + startY
        self.color = color

class Board:
    def __init__(self, rows, cols, startX, startY):

        self.NEUTRAL = (16, 27, 39)
        self.FRIENDLY = (24, 188, 156)
        self.ENEMY = (238, 102, 119)

        self.MOVES = 7

        self.rows = rows
        self.cols = cols
        self.startX = startX
        self.startY = startY
        self.distance = 100  # Hand calculated distance between each spot on site (approx.)
        self.move = True
        self.friendlySpots = 0
        self.enemySpots = 0
        self.board = self.createBoard()

    def createBoard(self):
        b = []
        for i in range(self.rows):
            b.append([])
            for j in range(self.cols):
                b[i].append(Spot(i, j, self.NEUTRAL, self.startX, self.startY, self.distance))
        return b

    def getColor(self, color):
        if color == self.FRIENDLY:
            return "F"
        elif color == self.ENEMY:
            return "E"
        return "N"

    def createTransposition(self):
        lastColor = self.board[0][0].color
        colorCount = 1
        transposition = ""
        for row in range(self.rows):
            for col in range(self.cols):
                if row == col == 0:
                    continue
                currSpot = self.board[row][col]
                if lastColor == currSpot.color:
                    colorCount += 1
                else:
                    if colorCount > 1:
                        transposition += str(colorCount)
                    self.getColor(lastColor)
                    lastColor = currSpot.color
                    colorCount = 1
        if colorCount > 1:
            transposition += str(colorCount)
        transposition += self.getColor(lastColor)
        return transposition


    def updateBoard(self):
        img = ImageGrab.grab(bbox=(0, 0, 1920, 1080))
        currEnemy = 0
        currFriendly = 0
        for row in range(self.rows):
            for col in range(self.cols):
                currSpot = self.board[row][col]
                pixelColor = img.getpixel((currSpot.posX, currSpot.posY))
                if currSpot.color != pixelColor:
                    currSpot.color = pixelColor
                if pixelColor == self.ENEMY:
                    currEnemy += 1
                elif pixelColor == self.FRIENDLY:
                    currFriendly += 1
        if currEnemy > self.enemySpots:
            self.move = True  # AI moves
        self.friendlySpots = currFriendly
        self.enemySpots = currEnemy

    def findAvailableMoves(self):
        available = []
        for col in range(self.cols):
            col = self.cols // 2 + (1 - 2 * (col % 2)) * (col + 1) // 2
            for row in range(self.rows - 1, -1, -1):
                if self.board[row][col].color == self.NEUTRAL:
                    available.append(self.board[row][col])
                    break
        return available

    def isDraw(self):
        occ = 0
        for row in self.board:
            for currSpot in row:
                if currSpot.color != self.NEUTRAL:
                    occ += 1
        return occ == (self.rows * self.cols), 0

    def gameEnded(self):
        b = self.board
        for row in range(self.rows):
            for col in range(self.cols - 3):
                if b[row][col].color == b[row][col + 1].color == b[row][col + 2].color == b[row][col + 3].color and b[row][col].color != self.NEUTRAL:
                    return (True, 123_456) if b[row][col].color == self.FRIENDLY else (True, -123_456)
        for col in range(self.cols):
            for row in range(self.rows - 3):
                if b[row][col].color == b[row + 1][col].color == b[row + 2][col].color == b[row + 3][col].color and b[row][col].color != self.NEUTRAL:
                    return (True, 123_456) if b[row][col].color == self.FRIENDLY else (True, -123_456)
        for row in range(self.rows - 3):
            for col in range(self.cols - 3):
                if b[row][col].color == b[row + 1][col + 1].color == b[row + 2][col + 2].color == b[row + 3][col + 3].color and b[row][col].color != self.NEUTRAL:
                    return (True, 123_456) if b[row][col].color == self.FRIENDLY else (True, -123_456)
        for row in range(self.rows - 3):  # Right to Left Diagonal
            for col in range(self.cols - 1, self.cols - 5, -1):
                if b[row][col].color == b[row + 1][col - 1].color == b[row + 2][col - 2].color == b[row + 3][col - 3].color and b[row][col].color != self.NEUTRAL:
                    return (True, 123_456) if b[row][col].color == self.FRIENDLY else (True, -123_456)
        return self.isDraw()

    def calculatePosition(self):
        friendlyConnections = [0, 0, 0, 0, 0]
        enemyConnections = [0, 0, 0, 0, 0]
        for row in range(self.rows):  # Left to Right
            for col in range(self.cols - 3):
                colors = []
                for i in range(4):
                    colors.append(self.board[row][col + i].color)
                friendlyScore = colors.count(self.FRIENDLY)
                enemyScore = colors.count(self.ENEMY)
                neutralScore = colors.count(self.NEUTRAL)
                if friendlyScore >= 1 and neutralScore + friendlyScore == 4:
                    friendlyConnections[friendlyScore] += 1
                if enemyScore >= 1 and neutralScore + enemyScore == 4:
                    enemyConnections[enemyScore] += 1
        for col in range(self.cols):  # Up to Down
            for row in range(self.rows - 3):
                colors = []
                for i in range(4):
                    colors.append(self.board[row + i][col].color)
                friendlyScore = colors.count(self.FRIENDLY)
                enemyScore = colors.count(self.ENEMY)
                neutralScore = colors.count(self.NEUTRAL)
                if friendlyScore >= 1 and neutralScore + friendlyScore == 4:
                    friendlyConnections[friendlyScore] += 1
                if enemyScore >= 1 and neutralScore + enemyScore == 4:
                    enemyConnections[enemyScore] += 1
        for row in range(self.rows - 3):  # Left to Right Diagonal
            for col in range(self.cols - 3):
                colors = []
                for i in range(4):
                    colors.append(self.board[row + i][col + i].color)
                friendlyScore = colors.count(self.FRIENDLY)
                enemyScore = colors.count(self.ENEMY)
                neutralScore = colors.count(self.NEUTRAL)
                if friendlyScore >= 1 and neutralScore + friendlyScore == 4:
                    friendlyConnections[friendlyScore] += 1
                if enemyScore >= 1 and neutralScore + enemyScore == 4:
                    enemyConnections[enemyScore] += 1
        for row in range(self.rows - 3):  # Right to Left Diagonal
            for col in range(self.cols - 1, self.cols - 5, -1):
                colors = []
                for i in range(4):
                    colors.append(self.board[row + i][col - i].color)
                friendlyScore = colors.count(self.FRIENDLY)
                enemyScore = colors.count(self.ENEMY)
                neutralScore = colors.count(self.NEUTRAL)
                if friendlyScore >= 1 and neutralScore + friendlyScore == 4:
                    friendlyConnections[friendlyScore] += 1
                if enemyScore >= 1 and neutralScore + enemyScore == 4:
                    enemyConnections[enemyScore] += 1
        friendlySum = friendlyConnections[1] * 10 + friendlyConnections[2] * 100 + friendlyConnections[3] * 1000
        enemySum = enemyConnections[1] * 10 + enemyConnections[2] * 100 + enemyConnections[3] * 1000
        return friendlySum - enemySum

    def makeMove(self):
        currScore = -math.inf
        spotToPlay = None
        for currSpot in self.findAvailableMoves():
            currSpot.color = self.FRIENDLY
            score = self.minimax(self.MOVES - 1, False, -math.inf, math.inf)
            currSpot.color = self.NEUTRAL
            if score > currScore:
                currScore = score
                spotToPlay = currSpot
        currX = spotToPlay.posX
        currY = spotToPlay.posY
        pyautogui.moveTo(currX, currY)
        pyautogui.leftClick()
        self.move = False
        pyautogui.moveTo(self.startX - self.distance, self.startY - self.distance)

    def minimax(self, moves, maximising, alpha, beta):
        ended, score = self.gameEnded()
        if ended:
            return score
        elif moves == 0:
            return self.calculatePosition()
        if maximising:  # True = AI moves, False = Enemy Moves
            bestScore = -math.inf
            for availableSpot in self.findAvailableMoves():
                availableSpot.color = self.FRIENDLY
                bestScore = max(bestScore, self.minimax(moves - 1, False, alpha, beta))
                availableSpot.color = self.NEUTRAL
                if bestScore >= beta:
                    break
                alpha = max(alpha, bestScore)
            return bestScore
        else:
            bestScore = math.inf
            for availableSpot in self.findAvailableMoves():
                availableSpot.color = self.ENEMY
                bestScore = min(bestScore, self.minimax(moves - 1, True, alpha, beta))
                availableSpot.color = self.NEUTRAL
                if bestScore <= alpha:
                    break
                beta = min(beta, bestScore)
            return bestScore