import os

import numpy as np
from keras import Model, Sequential, Input
from keras.layers import Dense, Reshape, Activation, BatchNormalization, Conv2D, Flatten, Dropout
from keras.optimizer_v2.adam import Adam
import tensorflow as tf
from numpy import ndarray

from NeuralNet import NeuralNet
from chess_game.ChessGame import ChessGame
from utils import dotdict

args = dotdict(
    {
        "lr": 0.001,
        "dropout": 0.3,
        "epochs": 1,
        "batch_size": 64,
        "cuda": tf.test.is_gpu_available(),
        "num_channels": 512,
    }
)


class ChessNetwork(NeuralNet):
    def __init__(self, game: ChessGame):
        super().__init__(game)
        self.game = game
        self.args = args
        self.model = self.get_model(game.getBoardSize(), game.getActionSize(), args)

    def train(self, examples):
        input_boards, target_pis, target_vs = list(zip(*examples))
        input_boards = np.asarray(input_boards)
        target_pis = np.asarray(target_pis)
        target_vs = np.asarray(target_vs)
        history = self.model.fit(
            x=input_boards,
            y=[target_pis, target_vs],
            batch_size=args.batch_size,
            epochs=args.epochs,
            verbose=0,
        )
        return history.history["pi_loss"][-1], history.history["v_loss"][-1]

    def predict(self, board):
        """
                board: np array with board
                """

        prep_board = ndarray.reshape(board, (1, 6, 8, 8))
        # run
        pi, v = self.model.predict(prep_board)
        return pi[0], v[0]

    def save_checkpoint(
            self, folder="checkpoint", filename="checkpoint.pth.tar"
    ):
        filepath = os.path.join(folder, filename)
        if not os.path.exists(folder):
            print(
                "Checkpoint Directory does not exist! Making directory {}".format(
                    folder
                )
            )
            os.mkdir(folder)
        self.model.save_weights(filepath)

    def load_checkpoint(
            self, folder="checkpoint", filename="checkpoint.pth.tar"
    ):
        # https://github.com/pytorch/examples/blob/master/imagenet/main.py#L98
        filepath = os.path.join(folder, filename)
        self.model.load_weights(filepath)

    def get_weights(self):
        pass

    def set_weights(self, weights):
        pass

    def request_gpu(self):
        return self.args.cuda

    def get_model(self, board_size, action_size, args):
        # game params
        planes, board_x, board_y = board_size
        action_size = action_size

        # Neural Net

        # s: batch_size x board_x x board_y
        input_boards = Input(shape=(planes, board_x, board_y))
        # batch_size  x board_x x board_y x 1
        x_image = Reshape((planes, board_x, board_y, 1))(input_boards)
        # batch_size  x board_x x board_y x num_channels
        h_conv1 = Activation("relu")(
            BatchNormalization(axis=3)(
                Conv2D(args.num_channels, 3, padding="same", use_bias=False)(
                    x_image
                )
            )
        )
        # batch_size  x board_x x board_y x num_channels
        h_conv2 = Activation("relu")(
            BatchNormalization(axis=3)(
                Conv2D(args.num_channels, 3, padding="same", use_bias=False)(
                    h_conv1
                )
            )
        )
        # batch_size  x (board_x-2) x (board_y-2) x num_channels
        h_conv3 = Activation("relu")(
            BatchNormalization(axis=3)(
                Conv2D(args.num_channels, 3, padding="valid", use_bias=False)(
                    h_conv2
                )
            )
        )
        # batch_size  x (board_x-4) x (board_y-4) x num_channels
        h_conv4 = Activation("relu")(
            BatchNormalization(axis=3)(
                Conv2D(args.num_channels, 3, padding="valid", use_bias=False)(
                    h_conv3
                )
            )
        )
        h_conv4_flat = Flatten()(h_conv4)
        # batch_size x 1024
        s_fc1 = Dropout(args.dropout)(
            Activation("relu")(
                BatchNormalization(axis=1)(
                    Dense(1024, use_bias=False)(h_conv4_flat)
                )
            )
        )
        # batch_size x 1024
        s_fc2 = Dropout(args.dropout)(
            Activation("relu")(
                BatchNormalization(axis=1)(Dense(512, use_bias=False)(s_fc1))
            )
        )
        # batch_size x action_size
        pi = Dense(action_size, activation="softmax", name="pi")(s_fc2)
        # batch_size x 1
        v = Dense(1, activation="tanh", name="v")(s_fc2)
        model = Model(inputs=input_boards, outputs=[pi, v])
        model.compile(
            loss=["categorical_crossentropy", "mean_squared_error"],
            optimizer=Adam(args.lr),
        )
        return model
