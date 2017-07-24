#!/usr/bin/python3)

import random
import numpy as np
from collections import defaultdict
from action import Action


class Agent:
    def __init__(self, p, pj, pn, height, width, areaMap):
        self.p = p
        self.p_small = (1 - p) / 4.0
        self.pj = pj  # p found jam if jam exists
        self.pn = pn  # p found jam if jam doesnt exists
        self.height = height
        self.width = width
        self.map = np.empty((height, width), dtype='str')
        self.exit_coord = None
        self.jams_coords = []
        self.prev = None

        for x in range(self.height):
            for y in range(self.width):
                self.map[x, y] = areaMap[x][y]

        # eqal prob
        self.hist = np.full((height, width), 1. / (height * width - 1))

        for (y, x), v in np.ndenumerate(self.hist):
            if self.map[y][x] == "W":
                self.hist[y, x] = 0
                self.exit_coord = (y, x)
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

    def __update_hist_after_move(self, move):
        new_hist = np.zeros((self.height, self.width))
        y_move, x_move = self.__get_move_coords(move)
        partial_sum = 0.0

        for (y, x), v in np.ndenumerate(self.hist):
            x_dest = (x + x_move) % self.width
            y_dest = (y + y_move) % self.height
            neigh_coords = self.__get_neighbors(y=y_dest, x=x_dest)

            p_dest = self.hist[y, x] * self.p
            if (y_dest, x_dest) != self.exit_coord:
                new_hist[y_dest, x_dest] += p_dest
                partial_sum += p_dest

            p_neigh = self.hist[y, x] * self.p_small
            for (y_neigh, x_neigh) in neigh_coords:
                if (y_neigh, x_neigh) != self.exit_coord:
                    new_hist[y_neigh, x_neigh] += p_neigh
                    partial_sum += p_neigh

        # normalization
        new_hist = new_hist / partial_sum

        self.hist = new_hist
        # print(np.sum(self.hist))

    @staticmethod
    def __get_move_coords(move):
        return {
            Action.UP: (-1, 0),
            Action.DOWN: (1, 0),
            Action.LEFT: (0, -1),
            Action.RIGHT: (0, 1)
        }.get(move, "error, action not found")

    def __get_neighbors(self, y, x):
        return [
            ((y - 1) % self.height, x),  # UP
            ((y + 1) % self.height, x),  # DOWN
            (y, (x + 1) % self.width),  # RIGHT
            (y, (x - 1) % self.width),  # LEFT
        ]

    def __get_move(self):
        max_coords = self.__get_max_coords()
        move_dict = defaultdict(int)

        for max_coord in max_coords:
            move_dict[self.__get_move_to_nearest_orientation_point(max_coord)] += 1

        return max(move_dict, key=lambda x: move_dict.get(x, 0))

    def __get_max_coords(self):
        # toleration must be increased
        indices = np.argwhere(np.isclose(self.hist, self.hist.max()))
        return indices

    def __get_move_to_nearest_orientation_point(self, coord):
        orientation_point = self.__get_nearest_orientation_point(coord)
        
        # print(orientation_point)
        # move = self.__get_
        coord_y, coord_x = coord
        dest_y, dest_x = orientation_point

        if dest_y - coord_y >= 0:
            dist_down = dest_y - coord_y
            dist_up = self.height - dest_y + coord_y
        else:
            dist_down = self.height - dest_y + coord_y
            dist_up = abs(dest_y - coord_y)

        if dest_x - coord_x >= 0:
            dist_left = self.width - dest_x + coord_x
            dist_right = dest_x - coord_x
        else:
            dist_left = self.width - dest_x + coord_x
            dist_right = abs(dest_x - coord_x)

        if dist_left >= dist_right:
            if dist_right != 0 and self.prev != Action.LEFT:
                return Action.RIGHT
        else:
            if dist_left != 0 and self.prev != Action.RIGHT:
                return Action.LEFT

        if dist_up >= dist_down:
            if dist_down != 0: # and self.prev != Action.UP:
                return Action.DOWN
        else:
            if dist_up != 0: # and self.prev != Action.DOWN:
                return Action.UP

        oposite_move = self.__get_oposite_move(self.prev)
        possible_moves = [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT]
        possible_moves.remove(oposite_move)

        return random.choice(possible_moves)

    def __get_nearest_orientation_point(self, coord):
        exit_dist = self.__get_distance_between(coord, self.exit_coord)
        exit_dist_full = np.sum(exit_dist)

        nearest_jams = []

        for jam_coord in self.jams_coords:
            jam_exit_dist = self.__get_distance_between(jam_coord, self.exit_coord)
            coord_jam_dist = self.__get_distance_between(jam_coord, coord)

            jam_exit_dist_full = np.sum(jam_exit_dist)
            coord_jam_dist_full = np.sum(coord_jam_dist)
            full_dist = jam_exit_dist_full + coord_jam_dist_full

            if full_dist <= exit_dist_full and coord_jam_dist_full != 0:
                nearest_jams.append((coord_jam_dist_full, jam_coord))

        if len(nearest_jams) == 0:
            return self.exit_coord
        else:
            return min(nearest_jams, key=lambda x: x[0])[1]

    def __get_distance_between(self, coords_1, coords_2):
        y_1, x_1 = coords_1
        y_2, x_2 = coords_2

        y_distance = min(abs(y_2 - y_1), y_1 + abs(self.height - y_2), y_2 + abs(self.height - y_1))
        x_distance = min(abs(x_2 - x_1), x_1 + abs(self.width - x_2), x_2 + abs(self.width - x_1))
        return y_distance, x_distance

    def __get_oposite_move(self, move):
        if move == Action.UP:
            return Action.DOWN
        elif move == Action.DOWN:
            return Action.UP
        elif move == Action.LEFT:
            return Action.RIGHT
        elif move == Action.RIGHT:
            return Action.LEFT
        else:
            print("Bad move sent to function: get oposite move")
            return None

    # nie zmieniac naglowka metody, tutaj agent decyduje w ktora strone sie ruszyc,
    # funkcja MUSI zwrocic jedna z wartosci [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT]
    def move(self):
        move = self.__get_move()
        self.__update_hist_after_move(move)
        self.prev = move
        return move
        # self.__update_hist_after_move(Action.LEFT)
        # return Action.LEFT

    # nie zmieniac naglowka metody, tutaj agent udostepnia swoj histogram (ten z filtru
    # histogramowego), musi to byc tablica (lista list, krotka krotek...) o wymarach takich jak
    # plansza, pobranie wartosci agent.histogram()[y][x] zwraca prawdopodobienstwo stania na polu
    # w wierszu y i kolumnie x
    def histogram(self):
        return self.hist
