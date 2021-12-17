import chess
import numpy as np


class AverageMeter(object):
    """From https://github.com/pytorch/examples/blob/master/imagenet/main.py"""

    def __init__(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def __repr__(self):
        return f'{self.avg:.2e}'

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count


class dotdict(dict):
    def __getattr__(self, name):
        return self[name]


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
