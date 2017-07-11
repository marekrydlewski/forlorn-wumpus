#!/usr/bin/python3)

import random
import numpy as np
from action import Action


class Agent:
    def __init__(self, p, pj, pn, height, width, areaMap):

        self.times_moved = 0
        self.direction = Action.LEFT

        self.p = p
        self.p_small = (1 - p) / 4.0
        self.pj = pj  # p found jam if jam exists
        self.pn = pn  # p found jam if jam doesnt exists
        self.height = height
        self.width = width
        self.map = np.empty((height, width), dtype='str')
        self.exit_coords = None
        self.jams_coords = []

        for x in range(self.height):
            for y in range(self.width):
                self.map[x, y] = areaMap[x][y]

        # eqal prob
        self.hist = np.full((height, width), 1. / (height * width - 1))

        for (y, x), v in np.ndenumerate(self.hist):
            if self.map[y][x] == "W":
                self.hist[y, x] = 0
                self.exit_coords = (y, x)
            elif self.map[y][x] == "J":
                self.jams_coords.append((y, x))

        return

    # nie zmieniac naglowka metody, tutaj agent dokonuje obserwacji swiata
    # sensor przyjmuje wartosc True gdy agent ma uczucie stania w jamie
    def sense(self, sensor):
        self.__update_hist_after_sense(sensor)

    def __update_hist_after_sense(self, sensor):
        pj_actual = self.pj if sensor is True else 1.0 - self.pj
        pn_actual = self.pn if sensor is True else 1.0 - self.pn
        partial_sum = 0.0

        for (y, x), v in np.ndenumerate(self.map):
            if v == "J":
                self.hist[y, x] *= pj_actual
            elif v == ".":
                self.hist[y, x] *= pn_actual
            else:
                self.hist[y, x] = 0
            partial_sum += self.hist[y, x]

        # normalization
        self.hist = self.hist / partial_sum

        # dup = np.sum(self.hist)
        # print(dup)

    def __update_hist_after_move(self, move):
        new_hist = np.zeros((self.height, self.width))
        x_move, y_move = self.__get_move_coords(move)
        partial_sum = 0.0

        for (y, x), v in np.ndenumerate(self.hist):
            x_dest = (x + x_move) % self.width
            y_dest = (y + y_move) % self.
            neigh_coords = self.__get_neighbors(y=y_dest, x=x_dest)

            if (y_dest, x_dest) != self.exit_coords:
                new_hist += self.hist[y_dest, x_dest] * self.p

            p_neigh = self.hist[y, x] * self.p_small
            for (y_neigh, x_neigh) in neigh_coords:
                if (y_neigh, x_neigh) != self.exit_coords:
                    new_hist[y_neigh, x_neigh] += p_neigh
                    partial_sum += p_neigh

        # normalization
        new_hist = new_hist / partial_sum

        self.hist = new_hist

    @staticmethod
    def __get_move_coords(self, move):
        return {
            Action.Up: (0, -1),
            Action.DOWN: (0, 1),
            Action.LEFT: (-1, 0),
            Action.RIGHT: (1, 0)
        }.get(move, "error, action not found")

    def __get_neighbors(self, y, x):
        return [
            ((y + 1) % self.height, x),  # UP
            ((y - 1) % self.height, x),  # DOWN
            (y, (x + 1) % self.width),  # RIGHT
            (y, (x - 1) % self.width),  # LEFT
        ]

    # nie zmieniac naglowka metody, tutaj agent decyduje w ktora strone sie ruszyc,
    # funkcja MUSI zwrocic jedna z wartosci [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT]
    def move(self):
        move = Action.DOWN
        self.__update_hist_after_move(move)
        if self.times_moved < self.width - 1:
            self.times_moved += 1
            return self.direction
        else:
            self.times_moved = 0
            self.direction = Action.RIGHT if self.direction == Action.LEFT else Action.LEFT
            return Action.DOWN

    # nie zmieniac naglowka metody, tutaj agent udostepnia swoj histogram (ten z filtru
    # histogramowego), musi to byc tablica (lista list, krotka krotek...) o wymarach takich jak
    # plansza, pobranie wartosci agent.histogram()[y][x] zwraca prawdopodobienstwo stania na polu
    # w wierszu y i kolumnie x
    def histogram(self):
        return self.hist
