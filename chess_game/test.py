import random

from chess_game.ChessGame import ChessGame, get_board

game = ChessGame()
board = game.getInitBoard()

player = 1

# make ten random moves
for _ in range(10):
    actions = game.getValidMoves(board, player)
    masked = []
    for i, move in enumerate(actions):
        if move == 1:
            masked.append(i)
    random_move = random.choice(masked)

    board, player = game.getNextState(board, player, random_move)
    print(board)

    print(get_board(board, player), end="\n---\n")

