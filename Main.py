import math
import csv
import abc
import copy
import os
import argparse
import sys
import time
from typing import *
from patterns import pattern_map

Matrix = List[List[int]]

def main() -> None:
    print("Conway's Game of Life https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life")
    args, initial_conditions = parse_args() 

    game = Game(args.tick_rate, game_of_life_rule, initial_conditions)

    game.run(args.evolutions)

class InitialConditionsBuilder:
    def __init__(self, width: int, height: int):
        self.state = [[0 for j in range(width)] for i in range(height)]

    def add_glider(self, x: int, y: int) -> Matrix:
        self._place(pattern_map['glider'], x, y)

    def add_from_placement_file(self, file_path):
        with open(file_path) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                pattern_matrix = pattern_map[row[0]]
                self._place(pattern_matrix, int(row[1]), int(row[2]))

    def _place(self, matrix: Matrix, x: int, y: int) -> None:
        ## TODO arg checking
        for row in range(len(matrix)):
            for column in range(len(matrix[0])):
                self.state[y + row][x + column] = matrix[row][column]

    def build(self) -> Matrix:
        return self.state

def parse_args() -> [argparse.Namespace, Matrix]:
    parser = argparse.ArgumentParser(description="Runs Conway's game of life in the terminal.") 
    parser.add_argument('-e', '--evolutions', default=16, type=int, help="The number of steps to run the game of life for.")
    parser.add_argument('-t', '--tick_rate', default=.3, type=float, help="The time between ticks in game (in seconds, default 0.3). Try something like 0.05 to watch the game evolve faster.")
    # TODO Add argument checking for width/height
    parser.add_argument('-w', '--width', default=100, type=int, help="The width (number of columns) of the game.")
    parser.add_argument('-r', '--rows', default=50, type=int, help="The height (number of rows) of the game.")
    parser.add_argument('--glider', action='store_true', required=False, help="Adds a simple glider to the game to give you an idea of what patterns are like.") 
    # TODO test placement file for compatibility with width/height
    parser.add_argument('-p','--placement_file', type=str, required=False, help="The location of the placement file. You can use these to place patterns into the game. Be sure the patterns fall within the allocated width/rows") 

    args = parser.parse_args()
    initial_conditions_builder = InitialConditionsBuilder(args.width, args.rows)

    if args.glider:
        initial_conditions_builder.add_glider(1, 1)
    if args.placement_file:
        initial_conditions_builder.add_from_placement_file(args.placement_file)

    return args, initial_conditions_builder.build()

def game_of_life_rule(state) -> Matrix:
    next_state = copy.deepcopy(state)

    # Function for looking up a cell at some position. The modulus here makes this game of life use a toriodal 
    # geometry. If you wanted to count out-of-bounds neighbors as dead instead, you could do that here.
    def neighbor(x: int, y: int) -> int:
        x_ = x % len(state[0])
        y_ = y % len(state)
        return state[y_][x_]

    # You could use convolutions or something else here for a fancier solution. I prefer this. I think it's easier to read.
    # The number of neighbors is computed by summing all of a cell's neighbors.
    def count_neighbors(x: int ,y: int) -> int:
        return neighbor(x-1,y-1) + neighbor(x,y-1) + neighbor(x+1, y-1) + \
                neighbor(x-1,y) + neighbor(x+1,y) + \
                neighbor(x-1, y+1) + neighbor(x,y+1) + neighbor(x+1, y+1)

    
    # There are some fancier approaches for computing a cell's behavior using binary operators. I prefer
    # these if-then statements; they're simpler to read.
    def rule_lookup(cell: int, neighbors_count: int) -> int:
        if cell:
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

    # Kind of a weird way of doing this in the terminal, I'll admit. 
    # Goes up row by row and erases each line of output.
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
