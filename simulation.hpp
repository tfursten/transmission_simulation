#ifndef SIMULATION_HPP
#define SIMULATION_HPP

#include "population.hpp"

Population *create_and_evolve_source(float mutation_rate, int carrying_capacity, 
                                              int genome_size, int generations);

Population *transmit_to_recipient(Population *source_pop, int bottleneck, 
                                                              int generations);

#endif