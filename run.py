###################################################################
# Original code by GitHub user joskvi
# Additions by Sean Whalen
# Last edit: Jun 13, 2018
###################################################################
import sys, getopt
import simulation_tools
import config
import random
try:
    import analysis_tools.py
except ImportError:
    pass

	
numChildren = 20
numGenerations = 15

# Function to sort maxdiff values and return array of indecies
#   in order from greatest to smallest
def sortMaxDiff(maxdiff):
	order = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
	values = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
	i = 1
	j = 0
	order[0] = 0
	values[0] = maxdiff[0]
	while i < 20:
		while j < i:
			if (maxdiff[i] >= values[j]):
				temp = i
				while (temp > j):
					order[temp] = order[temp-1]
					values[temp] = values[temp - 1]
					temp -= 1
				order[j] = i
				values[j] = maxdiff[i]
				j = i
			else:
				j += 1
				if (j == i):
					order[j] = i
					values[j] = maxdiff[i]
		
		j = 0
		i += 1
	
	return order


# Function to throw out worst 4 children pairs and randomly generate new ones
def throwOut(a,b,c,d,e,f,g,h):
	ret = [a,b,c,d,e,f,g,h]
	i = 0
	while i < 8:
		ret[i] = float(random.randint(100,450)) / 100
		i += 1
	return ret


# Function to perform effective bit recombination with children
def recombination(a,b,c,d,e,f,g,h):
	i = 0
	j = 0
	l = 0
	ret = [a,b,c,d,e,f,g,h]
	recombinationNumbers = [0.5, 0.25, 0.125, 0.0625, 0.03125, 0.015625, 0.0078125, 0.00390625]
	while i < 4:
		j = random.randint(3,7)
		l = random.randint(0,7)
		ret[i] += recombinationNumbers[l]
		ret[j] -= recombinationNumbers[l]
		i += 1
	i = 0
	while i < 8:
		if (ret[i] < 0):
			ret[i] = 0
		if (ret[i] > 5):
			ret[i] = 5
		i += 1
	return ret
	

# Function to perform effective bit mutation on effectively
#   more significant bits of children
def largeMutation(a,b,c,d,e,f,g,h):
	ret = [0,0,0,0,0,0,0,0]	# 8-numbers: 4 for Vb, 4 for Vdb
	largePotentialBits = [1, 0.5, 0.25, 0.125, -1, -0.5, -0.25, -0.125]
	rand = 0
	rand = random.randint(0,7)
	ret[0] = a + largePotentialBits[rand]
	rand = random.randint(0,7)
	ret[1] = b + largePotentialBits[rand]
	rand = random.randint(0,7)
	ret[2] = c + largePotentialBits[rand]
	rand = random.randint(0,7)
	ret[3] = d + largePotentialBits[rand]
	rand = random.randint(0,7)
	ret[4] = e + largePotentialBits[rand]
	rand = random.randint(0,7)
	ret[5] = f + largePotentialBits[rand]
	rand = random.randint(0,7)
	ret[6] = g + largePotentialBits[rand]
	rand = random.randint(0,7)
	ret[7] = h + largePotentialBits[rand]
	j = 0
	for i in ret:
		if i > 5:
			ret[j] = 5
		if i < 0:
			ret[j] = 0
		j += 1
	return ret
	

# Function to perform effective bit mutation on effectively
#   less significant bits of children
def smallMutation(a, b, c, d, one, two, three, four, five, six, seven, eight):
	ret = [0,0,0,0,0,0,0,0,0,0,0,0]	# 12-numbers: 6 for Vb, 6 for Vdb
	smallPotentialBits = [0.0625, 0.03125, 0.015625, -0.0625, -0.03125, -0.015625]
	rand = 0
	rand = random.randint(0,5)
	ret[0] = a + smallPotentialBits[rand]
	rand = random.randint(0,5)
	ret[1] = b + smallPotentialBits[rand]
	rand = random.randint(0,5)
	ret[2] = c + smallPotentialBits[rand]
	rand = random.randint(0,5)
	ret[3] = d + smallPotentialBits[rand]
	rand = random.randint(0,5)
	ret[4] = one + smallPotentialBits[rand]
	rand = random.randint(0,5)
	ret[5] = two + smallPotentialBits[rand]
	rand = random.randint(0,5)
	ret[6] = three + smallPotentialBits[rand]
	rand = random.randint(0,5)
	ret[7] = four + smallPotentialBits[rand]
	rand = random.randint(0,5)
	ret[8] = five + smallPotentialBits[rand]
	rand = random.randint(0,5)
	ret[9] = six + smallPotentialBits[rand]
	rand = random.randint(0,5)
	ret[10] = seven + smallPotentialBits[rand]
	rand = random.randint(0,5)
	ret[11] = eight + smallPotentialBits[rand]
	j = 0
	for i in ret:
		if i > 5:
			ret[j] = 5
		if i < 0:
			ret[j] = 0
		j += 1
	return ret
	

# Function for running the genetic algorithm function
#   runs until a child has been best for numGenerations (specified at top of file)
def sim_iterate():
	f = open('results.txt', 'w+')	# open/create file results.txt for writing
	# write headers to results.txt
	f.write("Gen# BestVB     BestVDB     MaxDiff      Gain        #GenBeenBest\n")

	i = 0
	gen = 0	 # counts number of overall generations
	max_in = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]	# used for according input diffs for maxDiffs
	results = []   # used for return of simulation_tools.run_simulations
	g = [0,0,0,0,0,0,0,0]	# Will be used for returns from genetic funtions
	vb = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]	# Children Vb values
	sort = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]  # sorting of maxDiff in sortMaxDiff()
	temp = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
	vdb = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]	# Children Vdb values
	maxDiff = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]	# Children grade values
	vb_best = vb[0]	# Keep track of Vb of best child pair
	vdb_best = vdb[0]	# Keep track of Vdb of best child pair
	beenBest = 0	# Keep track of num generations pair has been best child
	bestGrade = 0	# Keep track of grade of best child pair
	asc_file_path = config.LTSpice_asc_filename
	
	i = 0
	while i < numChildren:
		# Creates inital children randomly and tests them
		#	children in range 0-5 volts
		parameter = 'VDB'
		value = float(random.randint(0,500)) / 500
		vdb[i] = value
		simulation_tools.set_parameters(asc_file_path, parameter, value, True)
		parameter = 'VB'
		value = float(random.randint(0,500)) / 500
		vb[i] = value
		simulation_tools.set_parameters(asc_file_path, parameter, value, True)
		results = simulation_tools.run_simulations()
		print (i)
		maxDiff[i] = results[1]
		max_in[i] = results[0]
		print (maxDiff[i])
		#print(type(maxDiff[i]))
		i += 1
	
	while beenBest < numGenerations:
		beenBest += 1	# increment # generations maxDiff[0] has been best for
		gen += 1	# increment # generations total
			
		# Get sorted order of indexes for maxDiff
		sort = sortMaxDiff(maxDiff)

		# Sort VB via sorted order
		i = 0
		while (i < 20):
			temp[i] = vb[i]
			i += 1
		i = 0
		while (i < 20):
			vb[i] = temp[sort[i]]
			i += 1

		# Sort max_in via sorted order
		i = 0
		while (i < 20):
			temp[i] = max_in[i]
			i += 1
		i = 0
		while (i < 20):
			max_in[i] = temp[sort[i]]
			i += 1
			
		# Sort VDB via sorted order
		i = 0
		while (i < 20):
			temp[i] = vdb[i]
			i += 1
		i = 0
		while (i < 20):
			vdb[i] = temp[sort[i]]
			i += 1

		# Sort maxDiff via sorted order
		i = 0
		while (i < 20):
			temp[i] = maxDiff[i]
			i += 1			
		i = 0
		while (i < 20):
			maxDiff[i] = temp[sort[i]]
			i += 1

		# prints top 4 maxDiff values
		print("Top 4:")
		i = 0
		while (i < 4):
			print (maxDiff[i])
			i+=1
		
		# If maxDiff[0] is a new best, print to terminal & update values
		if (maxDiff[0] > bestGrade):
			print ("New Best Child")
			bestGrade = maxDiff[0]
			vb_best = vb[0]
			vdb_best = vdb[0]
			beenBest = 1
		
		# Print updates on beenBest and the best (VB, VDB, maxDiff)
		print ("Been Best for " + str(beenBest) + " generations")
		print ("Best VB = " + str(vb[0]) + " and Best VDB = " + str(vdb[0]))
		gain = maxDiff[0] / max_in[0]	# calculate the gain of the best child
		# write data info of best child to file results.txt
		f.write(str(gen) + "     " + str(vb[0]) + "    " + str(vdb[0]) + "   " + str(maxDiff[0]) + "  " + str(gain) + "  " + str(beenBest)+"\n")
		
		# Less significant bit mutations
		i = 0
		g = smallMutation(vb[2], vdb[2], vb[3], vdb[3], vb[4], vdb[4], vb[5], vdb[5], vb[6], vdb[6], vb[7], vdb[7])
		while i < 6:
			print (str(vb[i+2]) + ' ' + str(g[2*i]))
			vb[i+2] = g[2*i]
			print (str(vdb[i+2]) + ' ' + str(g[2*i + 1]))
			vdb[i+2] = g[2*i + 1]
			i+=1
	
		# More significant bit mutations
		i = 0
		g = recombination(vb[8], vdb[8], vb[9], vdb[9], vb[10], vdb[10], vb[11], vdb[11])
		while i < 4:
			print (str(vb[i+8]) + ' ' + str(g[2*i]))
			vb[i+8] = g[2*i]
			print (str(vdb[i+8]) + ' ' + str(g[2*i + 1]))
			vdb[i+8] = g[2*i + 1]
			i+=1
		
		# Recombinations (crossing one bit)
		i = 0
		g = largeMutation(vb[12], vdb[12], vb[13], vdb[13], vb[14], vdb[14], vb[15], vdb[15])
		while i < 4:
			print (str(vb[i+12]) + ' ' + str(g[2*i]))
			vb[i+12] = g[2*i]
			print (str(vdb[i+12]) + ' ' + str(g[2*i + 1]))
			vdb[i+12] = g[2*i + 1]
			i+=1
	
		# Throw out and generate new numbers
		i = 0
		g = throwOut(vb[16], vdb[16], vb[17], vdb[17], vb[18], vdb[18], vb[19], vdb[19])
		while i < 4:
			print (str(vb[i+16]) + ' ' + str(g[2*i]))
			vb[i+16] = g[2*i]
			print (str(vdb[i+16]) + ' ' + str(g[2*i + 1]))
			vdb[i+16] = g[2*i + 1]
			i+=1
		
		# Because of arrangement of while loop, only do this if beenBest for < numGenerations
		if (beenBest < numGenerations):
			i = 2
			while i < numChildren:
				# run simulation on children 2-19 (0 and 1 are saved, don't need to re-run)
				parameter = 'VDB'
				value = vdb[i]
				simulation_tools.set_parameters(asc_file_path, parameter, value, True)
				parameter = 'VB'
				value = vb[i]
				simulation_tools.set_parameters(asc_file_path, parameter, value, True)
				results = simulation_tools.run_simulations()
				print (i)
				maxDiff[i] = results[1]
				max_in[i] = results[0]
				print (maxDiff[i])
				i += 1
	f.close()
		
		

def simulate(filename=None, do_analysis=False):

    print("Runpy Simulate")
    results = []

    asc_file_path = config.LTSpice_asc_filename
    print ("filename is : " + asc_file_path)
    if filename is not None:
        # Parse the file containing the parameters
        command_list = simulation_tools.parse_parameter_file(filename)

        # Run the list of commands
        number_of_finished_simulations = 0
        all_filenames = []
        if command_list is None:
            print('Syntax error in parameter file.')
            return
        for command in command_list:
            if command[0] == 's':
                parameter = command[1]
                value = command[2]
                # Set parameter as specified
                print('Setting parameter:  ' + str(parameter) + '=' + str(value))
                simulation_tools.set_parameters(asc_file_path, parameter, value, True)
            if command[0] == 'r':
                parameter = command[1]
                parameter_values = command[2]
                # Run tests with the given parameter and corresponding list of parameter values
                # The filenames of the output data is returned
                results = simulation_tools.run_simulations([parameter, parameter_values], number_of_finished_simulations)
                filenames = results[0]
                print (filenames)
                print("Done Running Simulation")
                all_filenames.extend(filenames)
                number_of_finished_simulations += len(parameter_values)
                if do_analysis:
                    analyze(filenames)

        # If analysis made, make a report with all the analysied data
        if do_analysis:
            analysis_tools.make_report(all_filenames)
    else:
        # No parameter file is specified, run simulations with defaults values
        results = simulation_tools.run_simulations()



def analyze(filenames):
    # Any analysis to be done on the simulation results can be be coded here.
    for filename in filenames:
        analysis_tools.analyze_data(filename)

def help():
    print 'auto.py -r -f <parameterFile> -a\nUsing the option -a to analyze, requires -f to be set'

def main(argv):
    # Get arguments
    try:
        opts, args = getopt.getopt(argv, 'hrf:a', ['file=', 'run'])
    except getopt.GetoptError:
        print("This didn't work")
        help()
        sys.exit(2)


    # Parse arguments
    parameter_file = None
    do_analysis = False
    for opt, arg in opts:
        if opt == '-h':
            print("HFLAG")
            help()
            sys.exit()
        elif opt in ('-f', '--file'):
            parameter_file = arg
            print ("Param file is : "+arg)
        elif opt in ('-a'):
            do_analysis = True
        elif opt in ('-r', '--run'):
            sim_iterate()
            # old function replaced: simulate()
            sys.exit()


    # Run simulations based on arguments
    if parameter_file is not None:
        #print("This is the file " + parameter_file)
        simulate(parameter_file, do_analysis)

if __name__ == '__main__':
    main(sys.argv[1:])
