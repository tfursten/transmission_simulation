sim:
	clang++ -std=c++17 -Wall simulation.cpp population/population.cpp \
		population/genome.cpp utils.cpp -o sim

debug_sim:
	clang++ -std=c++17 -g -fsanitize=address -Wall simulation.cpp \
		population/population.cpp population/genome.cpp utils.cpp -o sim

test:
	clang++ -std=c++17 test.cpp -o test

clean:
	rm -rf sim test a.out sim.dSYM