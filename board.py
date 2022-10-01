import math

import pyautogui


class Spot:
    def __init__(self, row, col, color):
        self.row = col
        self.col = row
        self.color = color

class Board:
    def __init__(self, rows, cols, startX, startY):

        self.NEUTRAL = (16, 27, 39)
        self.FRIENDLY = (24, 188, 156)
        self.ENEMY = (238, 102, 119)

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
                b[i].append(Spot(i, j, self.NEUTRAL))
        return b

    def updateBoard(self):
        """

        Scans the board on site and matches it with the board in the code
        If number of enemy positions has increased, allows itself to make a move

        """
        currEnemy = 0
        currFriendly = 0
        for row in range(self.rows):
            for col in range(self.cols):
                currSpot = self.board[row][col]
                currX = (currSpot.row * self.distance) + self.startX
                currY = (currSpot.col * self.distance) + self.startY
                pixelColor = pyautogui.pixel(currX, currY)
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
            for row in range(self.rows - 1, -1, -1):
                if self.board[row][col].color == self.NEUTRAL:
                    available.append((row, col))
                    break
        return available

    def calculatePosition(self):
        scores = [0, 0, 0, 0]
        for row in range(self.rows):  # Left to Right
            for col in range(self.cols - 3):
                fScore, eScore = 0, 0
                for i in range(4):
                    currSpotColor = self.board[row][col + i].color
                    if currSpotColor == self.FRIENDLY:
                        fScore += 100
                        eScore = 0
                    elif currSpotColor == self.ENEMY:
                        fScore = 0
                        eScore += 100
                    else:
                        fScore += 10
                        eScore += 10
                if eScore >= 400:
                    return -math.inf
                elif fScore >= 400:
                    return math.inf
                scores[0] += (fScore - eScore)
        for col in range(self.cols):  # Up to Down
            for row in range(self.rows - 3):
                fScore, eScore = 0, 0
                for i in range(4):
                    currSpotColor = self.board[row + i][col].color
                    if currSpotColor == self.FRIENDLY:
                        fScore += 100
                        eScore = 0
                    elif currSpotColor == self.ENEMY:
                        fScore = 0
                        eScore += 100
                    else:
                        fScore += 10
                        eScore += 10
                if eScore >= 400:
                    return -math.inf
                elif fScore >= 400:
                    return math.inf
                scores[1] += (fScore - eScore)
        for row in range(self.rows - 3):  # Left to Right Diagonal
            for col in range(self.cols - 3):
                fScore, eScore = 0, 0
                for i in range(4):
                    currSpotColor = self.board[row + i][col + i].color
                    if currSpotColor == self.FRIENDLY:
                        fScore += 100
                        eScore = 0
                    elif currSpotColor == self.ENEMY:
                        fScore = 0
                        eScore += 100
                    else:
                        fScore += 10
                        eScore += 10
                if eScore >= 400:
                    return -math.inf
                elif fScore >= 400:
                    return math.inf
                scores[2] += (fScore - eScore)
        for row in range(self.rows - 3):  # Right to Left Diagonal
            for col in range(self.cols - 1, self.cols - 5, -1):
                fScore, eScore = 0, 0
                for i in range(4):
                    currSpotColor = self.board[row + i][col - i].color
                    if currSpotColor == self.FRIENDLY:
                        fScore += 100
                        eScore = 0
                    elif currSpotColor == self.ENEMY:
                        fScore = 0
                        eScore += 100
                    else:
                        fScore += 10
                        eScore += 10
                if eScore >= 400:
                    return -math.inf
                elif fScore >= 400:
                    return math.inf
                scores[3] += (fScore - eScore)
        return sum(scores)

    def gameEnded(self):
        occ = 0
        for row in self.board:
            for item in row:
                if item.color != self.NEUTRAL:
                    occ += 1
        return occ == (self.rows * self.cols)

    def makeMove(self):  # Move[0] = X, Move[1] = Y; Switch because IDK...
        score, move = self.minimax(6, True, -math.inf, math.inf, [])
        currX = (move[1] * self.distance) + self.startX
        currY = (move[0] * self.distance) + self.startY
        pyautogui.moveTo(currX, currY)
        print(score, move[0], move[1])
        pyautogui.leftClick()
        self.move = False
        pyautogui.moveTo(self.startX - self.distance, self.startY - self.distance)

    def minimax(self, moves, turn, alpha, beta, positions):
        if moves == 0 or self.gameEnded():
            return self.calculatePosition(), (-1, -1)
        if turn:  # True = AI moves, False = Enemy Moves
            bestScore = -math.inf
            bestMove = (-1, -1)
            availableMoves = self.findAvailableMoves()
            for move in availableMoves:
                row, col = move
                currSpot = self.board[row][col]
                currSpot.color = self.FRIENDLY
                score = self.minimax(moves - 1, False, alpha, beta, positions)[0]
                currSpot.color = self.NEUTRAL
                if score >= bestScore:
                    bestScore = score
                    bestMove = (row, col)
            return bestScore, bestMove
        else:
            bestScore = math.inf
            bestMove = (-1, -1)
            availableMoves = self.findAvailableMoves()
            for move in availableMoves:
                row, col = move
                currSpot = self.board[row][col]
                currSpot.color = self.ENEMY
                score = self.minimax(moves - 1, True, alpha, beta, positions)[0]
                currSpot.color = self.NEUTRAL
                if score <= bestScore:
                    bestScore = score
                    bestMove = (row, col)
            return bestScore, bestMove