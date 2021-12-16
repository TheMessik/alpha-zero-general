import chess
import numpy as np

from Game import Game


class ChessGame(Game):

    def __init__(self):
        super().__init__()
        self.board = chess.Board()

        self.action_names = {}

        counter = 0
        for square_from in chess.SQUARES:
            for square_to in chess.SQUARES:
                self.action_names[counter] = chess.Move(square_from, square_to)
                counter += 1

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

        decoded_move = self.action_names[action]

        piece = decoded_board.piece_at(decoded_move.from_square)
        decoded_board.remove_piece_at(decoded_move.from_square)
        decoded_board.set_piece_at(decoded_move.to_square, piece)
        return encode_board(decoded_board), -player

    def getValidMoves(self, board, player):
        decoded_board = get_board(board, player)
        valid_moves = np.zeros(shape=(self.getActionSize()))

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
        return [(board, pi)]

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


def get_board(encoded_board: np.array, player: int):
    decoded_board = chess.Board()

    for i, piece_name in enumerate(["K", "Q", "B", "N", "R", "P"]):
        section = encoded_board[i * 8: i * 8 + 8]

        for rank_num, rank in enumerate(section):
            for file_num, file in enumerate(rank):
                square = chess.square(file_num, rank_num)
                if file == 1:
                    adapted_piece = piece_name.upper()
                elif file == -1:
                    adapted_piece = piece_name.lower()
                else:
                    adapted_piece = None

                if adapted_piece is not None:
                    parsed_piece = chess.Piece.from_symbol(adapted_piece)
                    decoded_board.set_piece_at(square, parsed_piece)

    decoded_board.turn = player == 1

    return decoded_board


# b = chess.Board()
# b.push(chess.Move.from_uci("a2a4"))
# decode_board(encode_board(chess.Board()))
# print(b)

# game = ChessGame()

# board = chess.Board()
#
# print(board, end="\n---\n")
# move: chess.Move = list(board.legal_moves)[0]
# piece: chess.Piece = board.piece_at(move.from_square)
# board.remove_piece_at(list(board.legal_moves)[0].from_square)
# print(board, end="\n---\n")
# board.set_piece_at(move.to_square, piece)
# print(board)

# valids = game.getValidMoves(encode_board(chess.Board()), 1)
# print(chess.Move.from_uci("b2b3") in chess.Board().legal_moves)
# for i, move in enumerate(valids):
#     if move == 1:
#         print(f"Valid move: {game.action_names[i]}")
