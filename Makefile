FLAGS=-std=c++17 -Wall

sim:
	clang++ $(FLAGS) simulation/simulation.cpp simulation/population.cpp \
		simulation/genome.cpp -lboost_iostreams utils.cpp -o sim

debug_sim:
	clang++ $(FLAGS) -g -fsanitize=address simulation/simulation.cpp \
		simulation/population.cpp -lboost_iostreams simulation/genome.cpp \
		utils.cpp -o sim

analysis:
	clang++ $(FLAGS) analysis/sample.cpp analysis/transmission.cpp \
		utils.cpp -o analysis

clean:
	rm -rf sim test a.out sim.dSYM