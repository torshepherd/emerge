import pygame, numpy as np, math, csv

def draw_map(list_of_lists, top_left, tile_length):
	for j in range(len(list_of_lists)):
		for i in range(len(list_of_lists[j])):
			pygame.draw.rect(screen, COLOR_SCHEME[list_of_lists[j][i]], [top_left[0] + (i * tile_length), top_left[1] + (j * tile_length), tile_length, tile_length])
	pointlist = [top_left]
	pointlist.append([top_left[0] + (len(list_of_lists) * tile_length), top_left[1]])
	pointlist.append([top_left[0] + (len(list_of_lists) * tile_length), top_left[1] + (len(list_of_lists) * tile_length)])
	pointlist.append([top_left[0], top_left[1] + (len(list_of_lists) * tile_length)])
	pygame.draw.aalines(screen, WHITE, True, pointlist)

def draw_mini_map(list_of_lists, top_left, map_length):
	tile_length = map_length // len(list_of_lists)
	for j in range(len(list_of_lists)):
		for i in range(len(list_of_lists[j])):
			pygame.draw.rect(screen, COLOR_SCHEME[list_of_lists[j][i]], [top_left[0] + (map_length * (i / len(list_of_lists[j]))) // 1, top_left[1] + (map_length * (j / len(list_of_lists[j]))) // 1, tile_length, tile_length])
	pointlist = [top_left]
	pointlist.append([top_left[0] + map_length, top_left[1]])
	pointlist.append([top_left[0] + map_length, top_left[1] + map_length])
	pointlist.append([top_left[0], top_left[1] + map_length])
	pygame.draw.aalines(screen, WHITE, True, pointlist)

class Agent:
	def __init__(self, start_pos, name_ID, map_size):
		#Initialize column, row, and unique name ID (positive int)
		self.x = start_pos[0]
		self.y = start_pos[1]
		self.id = name_ID
		self.prev_index = 0

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
		self.moves = []
	
	def grab_map(self, other_agent):
		if other_agent != self.id:
			for bot in robots:
				if bot.id == other_agent:
					for row_i in range(len(bot.map)):
						for entry_i in range(len(bot.map[row_i])):
							if self.map[row_i][entry_i] == -1:
								self.map[row_i][entry_i] = bot.map[row_i][entry_i]

	def move(self, global_map):
		next_index = 0
		next_pos = []
		global interactions
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
				
			local_second_choice = list(local_options) #Just in case there are no unexplored tiles
			local_options_0 = list(local_options) #Create a copy of local_options to iterate through. Previously, this led to some errors where the for loop would skip the next item if an item was removed from it.
			
			for i in local_options_0:
				target_loc = global_map[self.y + directions[i][1]][self.x + directions[i][0]]
				map_loc = self.map[self.y + directions[i][1]][self.x + directions[i][0]]
				
				if i not in [self.prev_index - 1, self.prev_index, self.prev_index + 1]: #If diverges from path
					local_options.remove(i)
					continue

				if map_loc == -4: #If already been there
					local_options.remove(i)
					if target_loc > 0:
						self.map[self.y + directions[i][1]][self.x + directions[i][0]] = -4
						self.grab_map(target_loc)
						local_second_choice.remove(i)
						
				else: #If haven't been there
					if target_loc == -3:
						self.map[self.y + directions[i][1]][self.x + directions[i][0]] = target_loc
						local_options.remove(i)
						local_second_choice.remove(i)
						
					elif target_loc == -2:
						self.map[self.y + directions[i][1]][self.x + directions[i][0]] = target_loc
						next_pos = [self.x + directions[i][0], self.y + directions[i][1]]
						self.state = 1
						break
					
					elif target_loc > 0:
						self.map[self.y + directions[i][1]][self.x + directions[i][0]] = -4
						self.grab_map(target_loc)
						interactions += 1
						local_options.remove(i)
						local_second_choice.remove(i)
						
			if self.state == 0:
				if len(local_options) != 0:
					next_index = np.random.choice(local_options)
			
				elif len(local_second_choice) != 0:
					#print("retracing steps: ", self.id)
					next_index = np.random.choice(local_second_choice)

				else:
					#print("stuck: ", self.id)
					next_index = 8
				
				self.moves.append(next_index)
				next_pos = [self.x + directions[next_index][0], self.y + directions[next_index][1]]

		elif self.state == 1:
			#TODO: Add conditional for if self.trail[-1] has another robot in the way, don't move there.
			next_pos = self.trail.pop()

		#Vacate durrent position to 'explored'
		self.map[self.y][self.x] = -4

		#Set previous index to be current index
		self.prev_index = next_index
		
		#Add current position to the robot's trail
		self.trail.append([self.x, self.y])
		
		#Set cursor to next position
		self.x, self.y = next_pos
		
		#Write in id at new position
		self.map[self.y][self.x] = self.id

BLACK  = (  0,   0,   0)
RED    = (255,   0,   0)
GREEN  = (  0, 255,   0)
BLUE   = (  0,   0, 255)
ORANGE = (255, 255,   0)
CYAN   = (  0, 255, 255)
PURPLE = (255,   0, 255)
WHITE  = (255, 255, 255)
GREY_1 = ( 75,  75,  75)
GREY_2 = (150, 150, 150)

COLOR_SCHEME = {
	-4: GREY_2,
	-3: GREY_1,
	-2: ORANGE,
	-1: BLACK,
	 0: WHITE,
	 1: RED,
	 2: GREEN,
	 3: BLUE,
	 4: CYAN
}

def closest_minimaps(number_of_agents):
	return ((math.sqrt(number_of_agents - 1) // 1) + 1) ** 2

directions = [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]

#FPS = 60

trials = []
start_n_agents = int(input("Number of agents to start with: "))
incr_n_agents = int(input("Number of agents to increment by: "))
finish_n_agents = int(input("Number of agents to finish with: "))
start_n_tile_side = int(input("Number of tiles/side to start with: "))
incr_n_tile_side = int(input("Number of tiles/side to increment by: "))
finish_n_tile_side = int(input("Number of tiles/side to finish with: "))
n_trials = int(input("Number of trials for each: "))
file_name = input("File name: ")

for var_tiles in range(start_n_tile_side, finish_n_tile_side + incr_n_tile_side, incr_n_tile_side):
	for var_agents in range(start_n_agents, finish_n_agents + incr_n_agents, incr_n_agents):
		for trial in range(n_trials):
			trials.append([var_agents, var_tiles])

app_exit = False

MAP_PIX = 400
SCREEN_SIZE = (MAP_PIX * 2, MAP_PIX)

pygame.init()

screen = pygame.display.set_mode(SCREEN_SIZE)

pygame.display.set_caption("Graphic Emerge Simulation")

clock = pygame.time.Clock()

#------------------------------ Begin Sim Code ------------------------------
for trial_index in range(len(trials)):
	if app_exit:
		break

	n_agents, n_tile_side = trials[trial_index]

	#n_agents = int(input("Number of agents (must be square and even for now): "))
	#n_tile_side = int(input("Dimension of map (sidelength in # of tiles, must be factor of MAP_PIX for now): "))

	for i in range(n_agents):
		COLOR_SCHEME[i + 1] = COLOR_SCHEME[(i % 4) + 1]

	minimap_pix = MAP_PIX // math.sqrt(closest_minimaps(n_agents))
	map_tile_pix = MAP_PIX // n_tile_side
	minimap_tile_pix = minimap_pix // n_tile_side
	minimap_top_lefts = []
	size = [n_tile_side, n_tile_side]

	for j in range(int(math.sqrt(closest_minimaps(n_agents)))):
		for i in range(int(math.sqrt(closest_minimaps(n_agents)))):
			minimap_top_lefts.append([MAP_PIX + (minimap_pix * i), minimap_pix * j])

	done = False
	solve_steps = 0
	interactions = 0

	reference_map = []
	for i in range(size[1]):
		reference_map.append([0] * size[0])

	black_map = []
	for i in range(size[1]):
		black_map.append([-1] * size[0])

	empty_map = list(reference_map)

	#Adding items
	reference_map[(9 * size[1]) // 10][9 * size[0] // 10] = -2

	#Adding obstacles
	reference_map[size[1] // 3][size[0] // 3] = -3
	reference_map[size[1] // 3][(2 * size[0]) // 3] = -3
	reference_map[(2 * size[1]) // 3][size[0] // 3] = -3
	reference_map[(2 * size[1]) // 3][(2 * size[0]) // 3] = -3

	#robots = [Agent([2, 2], 1, size), Agent([2, size[1] - 3], 2, size), Agent([size[0] - 3, size[1] - 3], 3, size), Agent([size[0] - 3, 2], 4, size)]
	robots = []
	for i in range(n_agents):
		robots.append(Agent([int(size[0] // 10) + (2 * i), (size[1] // 10)], i + 1, size))

	for bot in robots:
		reference_map[bot.y][bot.x] = bot.id

	screen.fill(BLACK)
	
	while not done:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				done = True
				app_exit = True
				print('Sim cancelled. \nnumber of bots:', n_agents, '\ntiles per side:', n_tile_side, '\nsteps to solve:', solve_steps)

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					pass

		solve_steps += 1

		for bot in robots:
			previous_position = [bot.x, bot.y]
			bot.move(reference_map)
			reference_map[previous_position[1]][previous_position[0]] = 0
			reference_map[bot.y][bot.x] = bot.id

			if bot.state == 1:
				done = True
				print('number of bots:', n_agents, '\ntiles per side:', n_tile_side, '\nsteps to solve:', solve_steps, '\ninteractions:', interactions)
				trials[trial_index].append(solve_steps)
				trials[trial_index].append(interactions)

		draw_map(reference_map, [0,0], map_tile_pix)
	#	draw_map(reference_map, [0,0], MAP_PIX)
		for bot_i in range(len(robots)):
	#		draw_map(robots[bot_i].map, minimap_top_lefts[bot_i], minimap_tile_pix)
			draw_mini_map(robots[bot_i].map, minimap_top_lefts[bot_i], minimap_pix)
		
		pygame.display.flip()
	#	clock.tick(FPS)

pygame.quit()

with open(file_name + '.csv', 'w', newline='') as csvfile:
    filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for trial in trials:
    	filewriter.writerow(trial)