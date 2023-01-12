FLAGS=-std=c++17 -Wall
DEBUG_FLAGS=-std=c++17 -Wall -g -fsanitize=address

sim:
	clang++ $(FLAGS) simulation/simulation.cpp simulation/population.cpp \
		simulation/genome.cpp -lboost_iostreams utils.cpp -o sim

sim_monsoon:
	clang++ $(FLAGS) simulation/simulation.cpp simulation/population.cpp \
		simulation/genome.cpp utils.cpp -lz ./libboost_iostreams.a -o sim
	  
debug_sim:
	clang++ $(DEBUG_FLAGS) simulation/simulation.cpp \
		simulation/population.cpp -lboost_iostreams simulation/genome.cpp \
		utils.cpp -o sim

clean:
	rm -rf sim analyze a.out sim.dSYM/