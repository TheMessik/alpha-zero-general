import chess
import numpy as np

from Game import Game
from utils import encode_board


# encodings and mirror_move based on
# https://github.com/yeekit24/alpha-zero-general/blob/3fa23d76ed618f732e9485bd1bd6a44835e353a5/_chess/ChessGame.py
def from_move(move: chess.Move):
    return move.from_square * 64 + move.to_square


def to_move(action: int):
    to_sq = action % 64
    from_sq = int(action / 64)
    return chess.Move(from_sq, to_sq)


def mirror_move(move: chess.Move):
    return chess.Move(chess.square_mirror(move.from_square), chess.square_mirror(move.to_square))


class ChessGame(Game):

    def __init__(self):
        super().__init__()
        self.board = chess.Board()
        self.encoded_board = encode_board(self.board)

        self.action_names = {}

        counter = 0
        for square_from in chess.SQUARES:
            for square_to in chess.SQUARES:
                self.action_names[counter] = chess.Move(square_from, square_to)
                counter += 1

    def getInitBoard(self):
        return self.board

    def getBoardSize(self):
        return self.encoded_board.shape

    def getActionSize(self):
        # an action is a move from any square to any square
        # ergo, total number of actions is 64^2
        return pow(8 * 8, 2)

    def get_action_names(self):
        return self.action_names

    def getNextState(self, board: chess.Board, player, action):
        decoded_move = to_move(action)

        if not board.turn:
            decoded_move = mirror_move(decoded_move)

        b = board.copy()
        b.push(decoded_move)

        return b, -player

    def getValidMoves(self, board: chess.Board, player):
        valid_moves = np.zeros(shape=(self.getActionSize()))

        for move in board.legal_moves:
            move_index = from_move(move)
            valid_moves[move_index] = 1

        return valid_moves

    def getGameEnded(self, board: chess.Board, player):

        if not board.is_game_over():
            return 0
        else:
            if board.outcome().winner is None:
                return 0.5

            return 1 if board.outcome().winner else -1

    def getCanonicalForm(self, board: chess.Board, player):
        return board if board.turn else board.mirror()

    def getSymmetries(self, board, pi):
        return [(board, pi)]

    def stringRepresentation(self, board: chess.Board):
        return board.fen()

    # for i, piece_name in enumerate(["K", "Q", "B", "N", "R", "P"]):
    #     section = encoded_board[i * 8: i * 8 + 8]
    #
    #     for rank_num, rank in enumerate(section):
    #         for file_num, file in enumerate(rank):
    #             square = chess.square(file_num, rank_num)
    #             if file == 1:
    #                 adapted_piece = piece_name.upper()
    #             elif file == -1:
    #                 adapted_piece = piece_name.lower()
    #             else:
    #                 adapted_piece = None
    #
    #             if adapted_piece is not None:
    #                 parsed_piece = chess.Piece.from_symbol(adapted_piece)
    #                 decoded_board.set_piece_at(square, parsed_piece)
    #
    # decoded_board.turn = player == 1
#
# b = chess.Board()
#
# b.push(chess.Move.from_uci("e2e4"))
# b.push(chess.Move.from_uci("e7e5"))
# print(b, end="\n---\n")
# encoded = encode_board(b)
# print(encoded)
# print(get_board(encoded, 1))
