import math
import abc
import copy
import os
import argparse
import sys
import time
from typing import *

Matrix = List[List[int]]

def main() -> None:
    print("GoL")
    args, initial_conditions = parse_args() 

    game = Game(args.tick_rate, game_of_life_rule, initial_conditions)

    game.run(args.evolutions)

#TODO
#class TwoDimensionalCARules(abc.ABC):
#    @abc.abstractmethod
#    def transform   
#
class InitialConditionsBuilder:

    def __init__(self, width: int, height: int):
        self.state = [[0 for j in range(width)] for i in range(height)]

    def add_glider(self, x: int, y: int) -> Matrix:
        glider = [[1,0,0], [0,1,1], [1,1,0]]
        self._place(glider, x, y)

    def _place(self, matrix: Matrix, x: int, y: int) -> None:
        ## TODO arg checking
        for row in range(len(matrix)):
            for column in range(len(matrix[0])):
                self.state[y + row][x + column] = matrix[row][column]
        #self._draw(self.state)

    def _draw(self, state: Matrix) -> None:
        key = {0: '-', 1: '*'}
        for row in state:
            print(''.join(key[cell] for cell in row))

    def build(self) -> Matrix:
        return self.state


def parse_args() -> [argparse.Namespace, Matrix]:
    parser = argparse.ArgumentParser(description="Runs Conway's game of life in the terminal.") 
    parser.add_argument('-e', '--evolutions', default=16, type=int, help="The number of steps to run the game of life for.")
    parser.add_argument('-t', '--tick_rate', default=.3, type=float, help="The time between ticks in game (in seconds, default 0.3).")
    # TODO Add argument checking for width/height
    parser.add_argument('-w', '--width', default=100, type=int, help="The width (number of columns) of the game.")
    parser.add_argument('-r', '--rows', default=50, type=int, help="The height (number of rows) of the game.")
    parser.add_argument('--glider', action='store_true', required=False) 
    # TODO custom array loader

    args = parser.parse_args()
    initial_conditions_builder = InitialConditionsBuilder(args.width, args.rows)

    if args.glider:
        initial_conditions_builder.add_glider(1, 1)

    return args, initial_conditions_builder.build()

def game_of_life_rule(state) -> Matrix:
    next_state = copy.deepcopy(state)

    def neighbor(x: int, y: int) -> int:
        x_ = x % len(state[0])
        y_ = y % len(state)
        #print("neighbor x: " + str(x) + " y: " + str(y) + " is " + " x_ " + str(x_) + " y_ " + str(y_))
        return state[y_][x_]

    def count_neighbors(x: int ,y: int) -> int:
        return neighbor(x-1,y-1) + neighbor(x,y-1) + neighbor(x+1, y-1) + \
                neighbor(x-1,y) + neighbor(x+1,y) + \
                neighbor(x-1, y+1) + neighbor(x,y+1) + neighbor(x+1, y+1)

    
    def rule_lookup(cell: int, neighbors_count: int) -> int:
        if cell:
            #print(neighbors_count)
            # 2. Any live cell with two or three live neighbours lives on to the next generation.
            if neighbors_count == 2 or neighbors_count == 3:
                return 1
            return 0
        else:
            # 4. Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.
            if neighbors_count == 3:
                return 1
        # 1. Any live cell with fewer than two live neighbours dies, as if by underpopulation.
        # 3. Any live cell with more than three live neighbours dies, as if by overpopulation.
        return 0

    for row in range(len(state)):
        for column in range(len(state[0])):
            cell = state[row][column]
            neighbors_count = count_neighbors(column, row)
            next_state[row][column] = rule_lookup(cell, neighbors_count)
#            print("Cell x: " + str(column) + " y: " + str(row) + " is " + str(cell) + \
#                    " neighbors: " + str(neighbors_count) + " next: " + str(next_state[row][column]))
#
    return next_state


class Game:
    def __init__(self, 
            tick_time: float, 
            transform: Callable[[Matrix], Matrix],
            initial_state: Matrix):
        self.tick_time = tick_time
        self.transform = transform
        self.state = initial_state

    def run(self, steps: int) -> None:
        step = 0

        while step < steps:
            if not step == 0:
                self._clear()
            self.state = self.transform(self.state)
            self._draw(self.state)
            time.sleep(self.tick_time)
            step += 1

    def _clear(self) -> None:
        up = '\x1b[1A'
        erase = '\x1b[2K'
        for row in range(len(self.state)):
            sys.stdout.write(up)
            sys.stdout.write(erase)

    def _draw(self, state: Matrix) -> None:
        key = {0: '-', 1: '*'}
        for row in state:
            print(''.join(key[cell] for cell in row))
                
if __name__ == "__main__":
    main()
