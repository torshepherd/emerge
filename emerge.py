#Map Legend:
#-3: Obstacle
#-2: Item
#-1: Empty
# 0: Unexplored
#>0: Agent

#State Legend:
# 0: Searching
# 1: Returning item to nest

#Direction Legend (0 is current position, 1 is next position/direction of travel:
#			 - - -  | - - -  | - - -  | - - 1  | - 1 -  | 1 - -  | - - -  | - - -
#			 - 0 -  | - 0 -  | - 0 1  | - 0 -  | - 0 -  | - 0 -  | 1 0 -  | - 0 -
#			 - 1 -  | - - 1  | - - -  | - - -  | - - -  | - - -  | - - -  | 1 - -

import numpy as np

directions = [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]

def flip_x(n):
	return (8 - n) % 8

def flip_y(n):
	if n < 5:
		return (4 - n)
	else:
		return 12 - n

class Agent:
	def __init__(self, start_pos, name_ID, map_size, dir_index = 2):
		#Initialize column, row, and unique name ID (positive int)
		self.x = start_pos[0]
		self.y = start_pos[1]
		self.id = name_ID

		#Initialize direction of travel with vec (index in list of directions) and vel ([delta_col, delta_row])
		self.vec = dir_index
		self.vel = directions[d]											#Set start velocity based on lookup table of directions

		#ext is the border indices of the map
		self.ext = [map_size[0] - 1, map_size[1] - 1]

		#Initialize internal limited map to list with mapsize[1] number of of lists, each of length mapsize[0]
		self.map = [[0] * map_size[0]] * map_size[1]

		#Label the starting location in the map the agent ID
		self.map[self.y][self.x] = self.id

		#Initialize agent to Searching state
		self.state = 0
	
	def ref_v(self):
		#Update velocity pair based on direction index vec
		self.vel = directions[self.vec]
	
	def update(self, global_map):
		#If searching
		if self.state == 0:
			#If at the column border, flip the x velocity
			if self.x == 0 and self.vel[0] == -1:
				self.vec = flip_x(self.vec)
			if self.x == self.ext[0] and self.vel[0] == 1:
				self.vec = flip_x(self.vec)
			
			#If at the row border, flip the y velocity
			if self.y == 0 and self.vel[1] == -1:
				self.vec = flip_y(self.vec)
			if self.y == self.ext[1] and self.vel[1] == 1:
				self.vec = flip_y(self.vec)

			#Update the velocity based on the possibly changed index
			self.ref_v()
			
			#Fill next_pos with the ID of whatever the next target location contains on the GLOBAL MAP
			next_pos = global_map[self.y + self.vel[1]][self.x + self.vel[0]]
			
			#If the next location contains an obstacle
			if next_pos == -3:
				#Mark the obstacle on the self map
				self.map[self.y + self.vel[1]][self.x + self.vel[0]] = -2
				self.wander()

			#If the next location contains an item
			if next_pos == -2:
				#Set current position to empty, update coordinates, set new position to ID
				self.map[self.y][self.x] = 0
				self.x += self.vel[0]
				self.y += self.vel[1]
				self.map[self.y][self.x] = self.id
				
				#Switch state to Returning
				self.state = 1

			#If the next location is empty
			if next_pos == -1:
				#Set current position to empty, update coordinates, set new position to ID
				self.map[self.y][self.x] = -1
				self.x += self.vel[0]
				self.y += self.vel[1]
				self.map[self.y][self.x] = self.id

			#If the next location contains another bot
			if next_pos > 0:
				self.wander()

		if self.state == 1:

	def wander(self):
		self.vec = (self.vec + 2*np.random.randint(2) - 1) % 8		#Increment or decrement the direction index by 1, rotating just slightly
		self.ref_v()

size = [20, 20]
reference_map = [[0] * size[0]] * size[1]
number_of_agents = 10

