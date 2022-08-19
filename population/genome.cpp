#include <vector>

#include "genome.hpp"
#include "../utils.h"

using std::vector;


Genome::Genome() {}
Genome::Genome(const Genome &copied) {
    mutations = copied.mutations;
}

void Genome::add_random_mutation(int genome_size) {
    int random_mutation = uniform_random_in_range(genome_size + 1, random_seed);
    mutations.push_back(random_mutation);
}

vector<int> Genome::get_mutations() {
    return mutations;
}