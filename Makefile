FLAGS=-std=c++17 -Wall
DEBUG_FLAGS=-std=c++17 -Wall -g -fsanitize=address

sim:
	clang++ $(FLAGS) \
		simulation/simulation.cpp simulation/population.cpp \
		simulation/genome.cpp utils.cpp \
		-o sim

debug_sim:
	clang++ $(DEBUG_FLAGS) \
		simulation/simulation.cpp simulation/population.cpp \
		simulation/genome.cpp utils.cpp \
		-o sim

tests:
	clang++ $(FLAGS) \
		tests.cpp utils.cpp simulation/genome.cpp simulation/population.cpp \
		-o tests


clean:
	rm -rf sim tests a.out sim.dSYM/
