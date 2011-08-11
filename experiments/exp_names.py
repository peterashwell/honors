from systematic import systematic_name
EXP_COMMANDS='experiment_commands'
EXP_NAMES='experiment_names'
command_file = open(EXP_COMMANDS)
name_file = open(EXP_NAMES, 'w')
for line in command_file:
	if line[0] == '#':
		name_file.write(line)
	else:
		name_file.write(systematic_name(line.strip())[0] + '\n')
command_file.close()
name_file.close()
