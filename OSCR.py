#     ___  ____   ____ ____  
#    / _ \/ ___| / ___|  _ \ 
#   | | | \___ \| |   | |_) |
#   | |_| |___) | |___|  _ < 
#    \___/|____/ \____|_| \_\
#                            
#Welcome to the source file of oscr-cpu
#     This file is made by RANAK
#BTW this is the 4th version of oscr
#Full form => Open Source CPU by Ranak

#important modules
import time
import pygame

#basic ui
print('''
+--------------------------------------------------------+
|                   WELCOME TO OSCR - 16                 |
|This is a cpu emulator made by Ranak                    |
|CPU specifications:                                     |
| Ram:262kb  | BUS SIZE:16-bits | 65535 lines of program |
|Clock speed: 1 khz   |   Stack size: 1024 * 65535 bits  |
|Please read the manual before using the emulator!       |
+--------------------------------------------------------+
''')

#reading the txt file
file_name = str(input("Please enter the file name: \n>>>"))
with open(file_name,'r') as file:
	raw_program = file.readlines()

#removing the useless parts
program = []
for x in range(len(raw_program)):
	raw_data = raw_program[x]
	data = raw_data.strip()
	program.append(data)

#----------------------------------------main functions for the cpu-------------------------------------
class main():
	#clock function
	def clock(tick,time_gap):
		time.sleep(time_gap)
		if (tick == 1):
			tick = 0
		elif (tick == 0):
			tick = 1
		return tick
	
	#counter function
	def counter(tick,count):
		if tick == 1:
			count += 1
		return count
	
	#function for making the work easy of creating a meory
	def create_memory(size):
		return [0] * size    #creating a list of memory
	
	def draw_screen():
		for y in range(HEIGHT):
			for x in range(WIDTH):
				color = (display_memory[y][x], display_memory[y][x], display_memory[y][x])  # Grayscale
				pygame.draw.rect(screen, color, (x * PIXEL_SIZE, y * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))
		pygame.display.flip()
	
	def clear_screen():
		global display_memory
		display_memory = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
		screen.fill((0, 0, 0))
		pygame.display.flip()

	# Example function to set a pixel (simulating CPU instruction)
	def set_pixel(x, y, brightness):
		if 0 <= x < WIDTH and 0 <= y < HEIGHT:
			display_memory[y][x] = brightness  # Brightness: 0-255

#-------------------------------------------------Control unit---------------------------------------------------------------
class control_unit():
	
# This code assigns the command
	def command_assigner(program, count):
		raw_command = program[count].strip()
		
		# Ignore full-line comments
		if raw_command.startswith("//") or raw_command.startswith("#"):
			return ["NOP"]  # Treat comment lines as NOP (No Operation)
		
		# Remove inline comments (anything after //)
		command = raw_command.split("//")[0].strip()
		
		# Split command into parts
		command = command.split('|')
		
		# Checking if the data is larger than 16-bits
		for i in range(len(command)):
			try:
				value = int(command[i])
				if value > 65535:
					print("--------ERROR! THE DATA IS ABOVE 16-BITS!---------")
					return ["HALT"]  # Force halt if value is too large
				command[i] = value
			except ValueError:
				pass  # Ignore non-integer values
		
		return command
	
	#This code executes the command
	def command_executor(command,count,register,ram,flag_register,sp,stack):
		
		#Screen functions
		#draw function
		if command[0] == 'DRAW':
			x = command[1]
			y = command[2]
			state = command[3]
			main.set_pixel(x,y,state)
			main.draw_screen()
		
		#Clear screen function
		if command[0] == 'CLS':
			main.clear_screen()
			main.draw_screen()
		
		#stack functions
		#push fUNCTION
		if command[0] == 'PUSH':
			if sp < 1023:
				stack[sp] = register[command[1]]
				sp += 1
			else:
				print("Stack Overflow!")
		
		#POP function
		if command[0] == 'POP':
			if sp > 0:
				sp -= 1
				register[command[1]] = stack[sp]
			else:
				print("Stack Underflow!")
		
		#Jump command code
		if command[0] == 'JMP':
			count = int(command[1]) - 1
		
		#----CONDITIONAL JUMPS----
		
		#JMP if negative
		if command[0] == 'JMPN':
			if flag_register == 'N':
				count = command[1] - 1
		
		#JMP if overflow
		if command[0] == 'JMPO':
			if flag_register == 'O':
				count = command[1] - 1
		
		#JMP if zero
		if command[0] == 'JMPZ':
			if flag_register == 'Z':
				count = command[1] - 1
		
		#JMP if neither zero nor negative
		if command[0] == 'JMPZ-N':
			if (flag_register != 'Z' and flag_register != 'N'):
				count = command[1] - 1
		
		#Adding stuff to registers
		if command[0] == 'MOV':
			
			#adding data to register
			if command[1] == 'REG':
				register[command[2]] = command[3]
			
			#adding data to ram
			if command[1] == 'RAM':
				ram[command[2]] = command[3]
		
		#Outputing the data in register
		if command[0] == 'OUT':
			if command[1] == 'REG':
				print(">>>",register[command[2]])
			if command[1] == 'RAM':
				print(">>>",ram[command[2]])
		
		#Acepting a data given by user and storing it in register
		if command[0] == 'INP':
			register[command[1]] = input(">>>")
		
		#ALU functions
		if command[0] == 'ALU':
			register,flag_register = alu(command,register)
		
		#Delay function code
		if command[0] == 'DEL':
			time.sleep(float(command[1]))
		
		#no operation function
		if command[0] == 'NOP':
			pass
		
		#functions for making a function in OSCR assembly easier
		#function for calling
		if command[0] == 'CALL':
			sp += 1
			stack[sp] = count
			count = command[1] - 1
		
		#return function
		if command[0] == 'RET':
			sp -= 1
			count = stack[sp] + 1
		
		#Data movement and Transfer functions
		if command[0] == 'R2R':
			#Shifts data from Register to ram
			if command[1] == 'RAM':
				ram[command[2]] = register[command[3]]
			
			#shifts data from Ram to Register
			if command[1] == 'REG':
				register[command[2]] = ram[command[3]]
			
		#Always keep this at last
		return command,count,register,ram,flag_register,sp,stack

#----------------------------------------ALU functions--------------------------------------------------
def alu(command,register):
	flag_register = ''
	
	#Arithmetic Operations:
	
	#addition function
	if command[1] == 'ADD':
		register[command[4]] = int(register[command[2]]) + int(register[command[3]])
	
	#subtraction function
	if command[1] == 'SUB':
		register[command[4]] = int(register[command[2]]) - int(register[command[3]])
	
	#Division function
	if command[1] == 'DIV':
		register[command[4]] = int(register[command[2]]) // int(register[command[3]])
	
	#Multiplication function
	if command[1] == 'MUL':
		register[command[4]] = int(register[command[2]]) * int(register[command[3]])
	
	#Logical shift:
	#logical shift left
	if command[1] == 'LSH':
		register[command[3]] = int(register[command[3]]) << int(command[2])
	
		#logical shift right
	if command[1] == 'RSH':
		register[command[3]] = int(register[command[3]]) >> int(command[2])
	
	#Increment function
	if command[1] == 'INC':
		register[command[2]] = int(register[command[2]]) + 1
	
	#Decrement function
	if command[1] == 'DEC':
		register[command[2]] = int(register[command[2]]) - 1
	
	#FLAGS
	if len(command) == 5:
		if register[command[4]] == 0:
			flag_register = 'Z'
		
		if register[command[4]] < 0:
			flag_register = 'N'
	
		if register[command[4]] >= 65535:
			flag_register = 'O'
	
	#Boolean logic:
	
	#AND function
	if command[1] == 'AND':
		register[command[4]] = (int(register[command[2]]) & int(register[command[3]]))
	
	#Or instruction
	if command[1] == 'OR':
		register[command[4]] = (int(register[command[2]]) | int(register[command[3]]))
	
	#XOR function
	if command[1] == 'XOR':
		register[command[4]] = (int(register[command[2]]) ^ int(register[command[3]]))
	
	#NOT function
	if command[1] == 'NOT':
		register[command[3]] = ~(int(register[command[2]]) & 0xFFFF)
	
	return register,flag_register

#important variables
register = main.create_memory(6)
ram      = main.create_memory(65535)
stack    = main.create_memory(1024)
SP = 0
time.sleep(1)
tick = 0
count = 0
command = ' '
time_gap = float(1/1000)
flag_register = ''

# Screen constants
WIDTH, HEIGHT = 256, 256  # Logical resolution
PIXEL_SIZE = 2  # Scale factor (2x2 pixels per logical pixel)
WINDOW_SIZE = (WIDTH * PIXEL_SIZE, HEIGHT * PIXEL_SIZE)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("OSCR-16 Grayscale Screen")
clock = pygame.time.Clock()

# Memory-mapped display (2D array)
display_memory = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]

#The main loop of cpu emulator
while command[0] != 'HALT':
	command = control_unit.command_assigner(program,count)
	tick = main.clock(tick,time_gap)
	count = main.counter(tick,count)
	if tick == 1:
		command,count,register,ram,flag_register,SP,stack = control_unit.command_executor(command,count,register,ram,flag_register,SP,stack)


print("\n\n-----------------The program ended!---------------------")
