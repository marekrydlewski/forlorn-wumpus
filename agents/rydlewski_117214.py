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
        self.pj = pj    # p found jam if jam exists
        self.pn = pn    # p found jam if jam doesnt exists
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

        for (x, y), v in np.ndenumerate(self.hist):
            if self.map[x][y] == "W":
                self.hist[x, y] = 0
                self.exit_coords = (x, y)
            elif self.map[x][y] == "J":
                self.jams_coords.append((x, y))

        return

    # nie zmieniac naglowka metody, tutaj agent dokonuje obserwacji swiata
    # sensor przyjmuje wartosc True gdy agent ma uczucie stania w jamie
    def sense(self, sensor):
        self.__update_hist_after_sense(sensor)

    def __update_hist_after_sense(self, sensor):
        pj_actual = self.pj if sensor is True else 1.0 - self.pj
        pn_actual = self.pn if sensor is True else 1.0 - self.pn
        partial_sum = 0.0

        for (x, y), v in np.ndenumerate(self.map):
            if v == "J":
                self.hist[x, y] *= pj_actual
            elif v == ".":
                self.hist[x, y] *= pn_actual
            else:
                self.hist[x, y] = 0
            partial_sum += self.hist[x, y]

        # normalization
        self.hist = self.hist/partial_sum

        # dup = np.sum(self.hist)
        # print(dup)

    # nie zmieniac naglowka metody, tutaj agent decyduje w ktora strone sie ruszyc,
    # funkcja MUSI zwrocic jedna z wartosci [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT]
    def move(self):
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
