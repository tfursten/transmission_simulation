#ifndef GENOME_HPP
#define GENOME_HPP

#include <vector>

extern int random_seed;

struct Genome {
    std::vector<int> mutations;
};

void add_random_mutation(Genome* genome, int genome_length);
Genome* copy_genome(Genome* genome);

#endif