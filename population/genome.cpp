#include <vector>

#include "genome.hpp"
#include "../utils.hpp"
#include <iostream>

using std::vector;

void add_random_mutation(Genome* genome, int genome_length) {
    int mutation = uniform_random_in_range(genome_length + 1, random_seed);
    genome->mutations.push_back(mutation);
}

Genome* copy_genome(Genome* genome) {
    Genome* copy = new Genome{};
    for (int mutation : genome->mutations) {
        copy->mutations.push_back(mutation);
    }
    return copy;
}