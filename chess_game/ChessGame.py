import chess
import numpy as np

from Game import Game


class ChessGame(Game):

    def __init__(self):
        super().__init__()
        self.board = chess.Board()
        self.action_names = {
            move.uci(): move for move in [chess.Move(x, y) for x in chess.SQUARES for y in chess.SQUARES]
        }

    def getInitBoard(self):
        return encode_board(self.board)

    def getBoardSize(self):
        return encode_board(self.board).shape

    def getActionSize(self):
        # an action is a move from any square to any square
        # ergo, total number of actions is 64^2
        return pow(8 * 8, 2)

    def get_action_names(self):
        return self.action_names

    def getNextState(self, board, player, action):
        decoded_board = get_board(board, player)

        decoded_action = self.action_names[action]

        decoded_board.push(decoded_action)

        return encode_board(decoded_board), player * -1

    def getValidMoves(self, board, player):
        decoded_board = get_board(board, player)
        valid_moves = np.array((1, self.get_action_size()))

        for i, move in enumerate(self.action_names.values()):
            if move in decoded_board.legal_moves:
                valid_moves[i] = 1

        return valid_moves

    def getGameEnded(self, board, player):
        decoded_board = get_board(board, player)

        if not decoded_board.is_game_over():
            return 0
        else:
            if decoded_board.result() == "1-0" and player == 1:
                return 1
            elif decoded_board.result == "0-1" and player == -1:
                return -1
            else:
                return .5

    def getCanonicalForm(self, board, player):
        return board

    def getSymmetries(self, board, pi):
        return board, pi

    def stringRepresentation(self, board):
        return get_board(board, chess.WHITE).fen()


def encode_board(board: chess.Board) -> np.array:
    planes = {
        "K": np.zeros((8, 8)),
        "Q": np.zeros((8, 8)),
        "B": np.zeros((8, 8)),
        "N": np.zeros((8, 8)),
        "R": np.zeros((8, 8)),
        "P": np.zeros((8, 8))
    }

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            symbol = piece.symbol()
            plane = planes[symbol.upper()]
            plane[chess.square_rank(square)][chess.square_file(square)] = 1 if symbol.upper() == symbol else -1

    return np.concatenate(list(planes.values()))


def decode_board(board: np.array) -> chess.Board:
    parsed_board = chess.Board()

    def parse_plane(plane: np.array, piece: str, real_board: chess.Board):
        for rank_num, rank in enumerate(plane):
            for file_num, file in enumerate(rank):
                square = chess.square(file_num, rank_num)
                if file == 1:
                    piece = piece.upper()
                else:
                    piece = piece.lower()
                parsed_piece = chess.Piece.from_symbol(piece.upper()) if file == 1 else chess.Piece.from_symbol(
                    piece.lower())

                real_board.set_piece_at(square, parsed_piece)

    for i, piece in enumerate(["K", "Q", "B", "N", "R", "P"]):
        plane = board[i * 8: i * 8 + 8]
        parse_plane(plane, piece, parsed_board)

    return parsed_board


def get_board(encoded_board: np.array, player: int):
    decoded_board = decode_board(encoded_board)
    decoded_board.turn = chess.WHITE if player == 1 else chess.BLACK

    return decoded_board

#
# b = Board()
# b.push(chess_game.Move.from_uci("a2a4"))
# decode_board(encode_board(Board()))
# print(b)
