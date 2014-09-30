# -*- coding: utf-8; -*-
#
# Copyright (c) 2014 Cyriaque 'Cisoun' Skrapits, http://cs.dyn.ch
#
# X Puzzle is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# X Puzzle is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with X Puzzle.  If not, see <http://www.gnu.org/licenses/>.

import itertools
import math
import platform
import random
import sys

"""
Using a getch method from https://stackoverflow.com/questions/510357/python-read-a-single-character-from-the-user
in order to avoid validing an input.
"""
class _Getch:
    """
    Gets a single character from standard input.  Does not echo to the screen.
    """
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


getch = _Getch()


"""
X Puzzle class
"""
class XPuzzle:

	"""
	Public constants
	"""

	""" Public constants """

	# Directions
	UP					= 0
	DOWN				= 1
	LEFT				= 2
	RIGHT				= 3

	MIN_SIZE			= 2

	""" Private constants """

	__LINE_TO_REMOVE	= 2 # Line to remove at each move.

	# Square decoration
	if platform.system() == "Windows":
		__SQR_START		= '['
		__SQR_START_WIN	= __SQR_START
		__SQR_END		= ']'
		__SQR_END_WIN	= __SQR_END
	else:
		__SQR_START		= '\033[42m\033[1;32m '
		__SQR_START_WIN	= '\033[41m\033[1;31m '
		__SQR_END		= ' \033[0m'
		__SQR_END_WIN	= __SQR_END


	"""
	Initializer
	"""
	def __init__(self, side):
		if side < self.MIN_SIZE: side = self.MIN_SIZE # Check the size.
		
		self.grid = []
		self.side = side
		self.size = side * side
		self.squareSize = 0

		self.__LINE_TO_REMOVE = self.__LINE_TO_REMOVE + side * 2

		self.__generateGrid()
		self.__hasToFlush = False
		self.__hasWon = False
		self.__squareDecoS = self.__SQR_START
		self.__squareDecoE = self.__SQR_END

	"""
	Check if the grid is ordered and the last square is empty
	"""
	def __check(self):
		# Look into the grid and check with an iterator if it is ordered.
		for x in range(0, self.side):
			for y in range(0, self.side):
				i = (x * self.side + y + 1) % self.size # 1,2,..,N,0 (iterator)
				if self.grid[x][y] != i: # ...not ordered.
					return False

		# If ordered, change square deco and return true.
		self.__squareDecoS = self.__SQR_START_WIN
		self.__squareDecoE = self.__SQR_END_WIN
		return True


	"""
	Create a random grid
	"""
	def __generateGrid(self):
		# Generate a list of random and unique numbers.
		numbers = list(range(0, self.size))
		random.shuffle(numbers)

		# Compute the squares size.
		self.squareSize = len(str(max(numbers)))
		
		# Fill the grid.
		for x in range(0, self.side):
			self.grid.append([])
			for y in range(0, self.side):
				self.grid[x].append(numbers.pop())

	"""
	Draw/write a square with a value at the middle
	"""
	def __generateSquare(self, value):
		if value > 0:
			# Draw a normal square.
			size = len(str(value))
			position = int((self.squareSize + 2) / 2) - int(size / 2) - 1 # Align the text at the middle.
			end = position + size
			return (
					self.__squareDecoS + 
					(' ' * position) + 
					str(value) + 
					(' ' * int(self.squareSize - end)) +
					self.__squareDecoE
				)
		else:
			# Draw an empty square.
			return ' ' * (self.squareSize + 2)

	"""
	Move a piece
	"""
	def move(self, direction):
		# Get the empty square's coords.
		x, y = 0, 0 # Coords
		for i in range(0, self.side):
			line = self.grid[i]
			y = i
			if 0 in line:
				x = line.index(0)
				break

		# Move dem squares !
		last = self.side - 1 # Last index
		if direction == self.UP and y < last:		# Move down the empty square.
			self.grid[y][x] = self.grid[y + 1][x]
			self.grid[y + 1][x] = 0
		elif direction == self.DOWN and y > 0:		# Move up the empty square. 
			self.grid[y][x] = self.grid[y - 1][x]
			self.grid[y - 1][x] = 0
		elif direction == self.LEFT and x < last: 	# Move right the empty square.
			self.grid[y][x] = self.grid[y][x + 1]
			self.grid[y][x + 1] = 0
		elif direction == self.RIGHT and x > 0: 	# Move left the empty square.
			self.grid[y][x] = self.grid[y][x - 1]
			self.grid[y][x - 1] = 0

		# Check if the player has won.
		self.__hasWon = self.__check()

	"""
	Run the game.
	"""
	def run(self):
		self.show()

		while not self.__hasWon:
			d = getch() # Capture the player's action.
			if d == chr(65): self.move(XPuzzle.UP)
			if d == chr(66): self.move(XPuzzle.DOWN)
			if d == chr(68): self.move(XPuzzle.LEFT)
			if d == chr(67): self.move(XPuzzle.RIGHT)
			if d in ['q', 'Q']: sys.exit(0)
			print()
			self.show()

		# End.
		print('Well done ! You won !\n')

	"""
	Show the grid
	"""
	def show(self):
		output = ''

		# Erase the last screen.
		# TODO: Check if it works on Windows.
		if self.__hasToFlush:
			for x in range(self.__LINE_TO_REMOVE):
				sys.stdout.write("\033[F")
		
		# Draw the new grid.
		for x in range(0, self.side):
			for y in range(0, self.side):
				square = self.__generateSquare(self.grid[x][y])
				output = output + square + ' '
			output = output + '\n\n'

		# Allow erasing last screen.
		self.__hasToFlush = True

		# Print the new screen.
		print(output)

"""
Main routine
"""
if __name__ == '__main__':
	# Intro.
	print()
	print('\033[1;31m☰☰☰ X PUZZLE ☰☰☰\033[0m')
	print('\033[0;3mCreated by Cyriaque Skrapits\033[0m')
	print()
	print('Use the arrows to move the pieces around the hole.')
	print('Press Q to quit.')
	print()
	size = int(input('Size (>=' + str(XPuzzle.MIN_SIZE) + ') : '))
	print()

	# Run the game.
	game = XPuzzle(size)
	game.run()