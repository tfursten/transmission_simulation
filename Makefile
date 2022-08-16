all:
	clang++  -std=c++11 simulation.cpp population.cpp utils.c -o run

test:
	clang++ -std=c++11 test.c -o test

clean:
	rm run test a.out