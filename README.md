# SeniorProject

This senior project is a command line tool that runs a genetic algorithm on a differential amplifier in LTSpice. It uses the algorithm to bias the circuit to acheive its greatest possible gain.

How to use

Download the files into the same directory as Python; you must have python to run this code (works with Python 2.7, not tested with other versions). The config.py must be configured to change the path of the location of LTSpice's executable.

python run.py -r

This command runs the program. Each child takes roughly 2-3 seconds to run, and each generation runs 18 children (outside of the first generation).

This code is configured to run on a LTSpice file with parameters VB and VDB, with the circuit being operated on having a lowest voltage of 0V and a highest voltage of 5V.

Information for each data point of a simulation is written to a .RAW file, which the program reads from. In config.py, the correct indecies for each data point must be selected, as they can correspond to different values depending on the simulation.

After each generation, information about the best child is written to a file named 'Results.txt,' which will continually fill until the system converges and the code terminates without error. An example is attached in this repository.
