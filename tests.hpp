#ifndef TESTS_HPP
#define TESTS_HPP

#include <vector>
#include "simulation/genome.hpp"

void test_uniform_random_in_range();
void test_poisson_dist();

void test_add_random_mutation();
void test_copy_genome();

void test_init_population();
void test_replicate_population();
void test_mutate_population();
void test_select_population();
void test_transmit();

int count_mutations_in_population(std::vector<Genome*>* population);

#endif