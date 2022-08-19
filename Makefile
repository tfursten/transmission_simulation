all:
	clang++  -std=c++11 simulation.cpp population/population.cpp \
		population/genome.cpp population/sample.cpp population/transmission.cpp \
		utils.c -o run

test:
	clang++ -std=c++11 test.c -o test

clean:
	rm run test a.out