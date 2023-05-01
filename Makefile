FLAGS=-std=c++17 -Wall
DEBUG_FLAGS=-std=c++17 -Wall -g -fsanitize=address

sim:
	clang++ $(FLAGS) \
		simulation/simulation.cpp simulation/population.cpp \
		simulation/genome.cpp utils.cpp \
		-o sim \
		-lboost_iostreams

sim_monsoon:
	clang++ $(FLAGS) \
		simulation/simulation.cpp simulation/population.cpp \
		simulation/genome.cpp utils.cpp \
		-o sim \
		-lz ./libboost_iostreams.a
	  
debug_sim:
	clang++ $(DEBUG_FLAGS) \
		simulation/simulation.cpp simulation/population.cpp \
		simulation/genome.cpp utils.cpp \
		-o sim \
		-lboost_iostreams

tests:
	clang++ $(FLAGS) \
		tests.cpp utils.cpp simulation/genome.cpp simulation/population.cpp \
		-o tests \
		-lboost_iostreams


clean:
	rm -rf sim analyze tests a.out sim.dSYM/
