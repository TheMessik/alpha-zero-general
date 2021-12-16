import chess
import numpy as np

from Game import Game


class ChessGame(Game):

    def __init__(self):
        super().__init__()
        self.board = chess.Board()
        self.encode_board = encode_board(self.board)

        self.action_names = {}

        counter = 0
        for square_from in chess.SQUARES:
            for square_to in chess.SQUARES:
                self.action_names[counter] = chess.Move(square_from, square_to)
                counter += 1

    def getInitBoard(self):
        return self.encode_board

    def getBoardSize(self):
        return self.encode_board.shape

    def getActionSize(self):
        # an action is a move from any square to any square
        # ergo, total number of actions is 64^2
        return pow(8 * 8, 2)

    def get_action_names(self):
        return self.action_names

    def getNextState(self, board, player, action):
        decoded_board = get_board(board, player)

        print(decoded_board, end="\n---\n")

        decoded_move = self.action_names[action]

        decoded_board.push(decoded_move)

        encoded = encode_board(decoded_board)

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
    planes = np.zeros((6, 8, 8), dtype=np.int8)

    for piece in chess.PIECE_TYPES:

        # find all white pieces on the board
        for square in board.pieces(piece, chess.WHITE):
            planes[piece - 1][chess.square_rank(square)][chess.square_file(square)] = 1

        # find all black pieces on the board
        for square in board.pieces(piece, chess.BLACK):
            planes[piece - 1][chess.square_rank(square)][chess.square_file(square)] = -1

    return planes


def get_board(encoded_board: np.array, player: int):
    decoded_board = chess.Board(fen="8/8/8/8/8/8/8/8 w - - 0 1")  # initialize to empty board

    for piece in chess.PIECE_TYPES:
        plane = encoded_board[piece - 1]
        for rank_num, rank in enumerate(plane):
            for file_num, file in enumerate(rank):
                if file != 0:
                    adapted_piece = chess.Piece(piece, chess.WHITE if file == 1 else chess.BLACK)
                    decoded_board.set_piece_at(rank_num * 8 + file_num, adapted_piece)

    decoded_board.turn = player == 1

    return decoded_board


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

b = chess.Board()

b.push(chess.Move.from_uci("e2e4"))
b.push(chess.Move.from_uci("e7e5"))
print(b, end="\n---\n")
encoded = encode_board(b)
print(encoded)
print(get_board(encoded, 1))
