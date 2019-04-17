#Map Legend:
#-3: Obstacle
#-2: Item
#-1: Unexplored
# 0: Empty
#>0: Agent

#State Legend:
# 0: Searching
# 1: Returning item to nest

#Direction Legend (0 is current position, 1 is next position/direction of travel:
#			 - - -  | - - -  | - - -  | - - 1  | - 1 -  | 1 - -  | - - -  | - - -
#			 - 0 -  | - 0 -  | - 0 1  | - 0 -  | - 0 -  | - 0 -  | 1 0 -  | - 0 -
#			 - 1 -  | - - 1  | - - -  | - - -  | - - -  | - - -  | - - -  | 1 - -

#local_env Legend:
#5 4 3
#6 - 2
#7 0 1

import numpy as np

directions = [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]

#Not used in search-instead-of-velocity
def flip_x(n):
	return (8 - n) % 8

#Not used in search-instead-of-velocity
def flip_y(n):
	if n < 5:
		return (4 - n)
	else:
		return 12 - n

#Function to calculate the center of mass of a space where 0 represents matter and any other number represents something not taken into account
#Not used in search-instead-of-velocity
def center_of_mass(space):
	numer_x = 0
	denom_x = 0
	numer_y = 0
	denom_y = 0

	for i in range(len(space)):
		for j in range(len(space[i])):
			if space[i][j] == 0:
				numer_x += j
				numer_y += i
				denom_x += 1
				denom_y += 1

	return [numer_x/denom_x, numer_y/denom_y]

def print_map(list_of_lists):
	for row in list_of_lists:
		print(''.join(((' ')*(3-len(str(entry)))+str(entry)) for entry in row))
	print('')

class Agent:
	def __init__(self, start_pos, name_ID, map_size, dir_index = 1):
		#Initialize column, row, and unique name ID (positive int)
		self.x = start_pos[0]
		self.y = start_pos[1]
		self.id = name_ID

		#Initialize direction of travel with vec (index in list of directions) and vel ([delta_col, delta_row])
		self.vec = dir_index
		self.vel = directions[dir_index]

		#ext is the border indices of the map
		self.ext = [map_size[0] - 1, map_size[1] - 1]

		#Initialize internal limited map to list with mapsize[1] (y dimension) number of of lists, each of length mapsize[0] (x dimension)
		self.map = []
		for i in range(map_size[1]):
			self.map.append([-1] * map_size[0])

		#Label the starting location in the map the agent ID
		self.map[self.y][self.x] = self.id

		#Initialize agent to Searching state
		self.state = 0

		#Initialize trail of positions for retracing steps
		self.trail = []
	
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
			pass
	def grab_map(self, other_agent):
		if other_agent != self.id:
			pass

	def move(self, global_map):
		next_pos = []
		if self.state == 0:
			local_options = list(range(8))
			
			if self.x == 0:
				local_options.remove(5)
				local_options.remove(6)
				local_options.remove(7)
			
			if self.x == self.ext[0]:
				local_options.remove(1)
				local_options.remove(2)
				local_options.remove(3)
			
			if self.y == 0:
				try:
					local_options.remove(3)
				except ValueError:
					pass
				local_options.remove(4)
				try:
					local_options.remove(5)
				except ValueError:
					pass
			
			if self.y == self.ext[1]:
				try:
					local_options.remove(7)
				except ValueError:
					pass
				local_options.remove(0)
				try:
					local_options.remove(1)
				except ValueError:
					pass
			
			for i in local_options:
				target_loc = global_map[self.y + directions[i][1]][self.x + directions[i][0]]
				self.map[self.y + directions[i][1]][self.x + directions[i][0]] = target_loc
				
				if (target_loc == -3) or (target_loc == self.id):
					local_options.remove(i)
				
				elif target_loc == -2:
					next_pos = [self.x + directions[i][0], self.y + directions[i][1]]
					self.state = 1
					break
				
				elif target_loc > 0:
					self.grab_map(target_loc)
					local_options.remove(i)

			if self.state == 0:
				next_index = np.random.choice(local_options)
				next_pos = [self.x + directions[next_index][0], self.y + directions[next_index][1]]
		
		elif self.state == 1:
			#TODO: Add conditional for if self.trail[-1] has another robot in the way, don't move there.
			next_pos = self.trail.pop()

		#Vacate durrent position
		self.map[self.y][self.x] = 0
		
		#Add current position to the robot's trail
		self.trail.append([self.x, self.y])
		
		#Set cursor to next position
		self.x, self.y = next_pos
		
		#Write in id at new position
		self.map[self.y][self.x] = self.id

#Initializing map
size = [11, 11]
reference_map = []
for i in range(size[1]):
	reference_map.append([0] * size[0])

#Adding items (places 1 item in the middle if odd map size)
reference_map[size[1] // 2][size[0] // 2] = -2

#Adding obstacles
reference_map[size[1] // 3][size[0] // 3] = -3
reference_map[size[1] // 3][(2 * size[0]) // 3] = -3
reference_map[(2 * size[1]) // 3][size[0] // 3] = -3
reference_map[(2 * size[1]) // 3][(2 * size[0]) // 3] = -3

items_found = False

robots = [Agent([2, 2], 1, size, 1), Agent([2, size[1] - 3], 2, size, 3), Agent([size[0] - 3, size[1] - 3], 3, size, 5), Agent([size[0] - 3, 2], 4, size, 7)]

for bot in robots:
	reference_map[bot.y][bot.x] = bot.id

while not items_found:
	print_map(reference_map)

	if input("Press return to iterate or type 1 to view agent maps >> ") != '':
		for bot in robots:
			print_map(bot.map)

	for bot in robots:
		previous_position = [bot.x, bot.y]
		bot.move(reference_map)
		reference_map[previous_position[1]][previous_position[0]] = 0
		reference_map[bot.y][bot.x] = bot.id
		
		if bot.state == 1:
			items_found = True
			break

	
input("Item found! Press return to exit... ")