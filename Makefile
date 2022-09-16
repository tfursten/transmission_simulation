all:
	clang++  -std=c++17 simulation.cpp population/population.cpp \
		population/genome.cpp population/sample.cpp population/transmission.cpp \
		utils.cpp -o run

test:
	clang++ -std=c++17 test.cpp -o test

clean:
	rm run test a.out