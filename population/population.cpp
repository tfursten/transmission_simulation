#include <vector>
#include <stdio.h>
#include <cmath>

#include "population.hpp"
#include "../utils.hpp"

using std::vector;


Population::Population(double mutation_rate, int carrying_capacity, 
                                               int generations, int genome_size) 
    : mutation_rate {mutation_rate}, 
      carrying_capacity {carrying_capacity}, 
      generations {generations},
      genome_size {genome_size} 
{
    Genome founder;
    genomes.push_back(founder);
}

Population::Population(const Population &source, int bottleneck, 
                                                                int generations) 
    : mutation_rate {source.mutation_rate},
      carrying_capacity {source.carrying_capacity},
      genome_size {source.genome_size},
      generations {generations},
      bottleneck {bottleneck}
{ 
    int selected;
    for (int i = 0; i < bottleneck; i++) {
        selected = uniform_random_in_range(source.genomes.size(), random_seed);
        genomes.push_back(Genome(source.genomes[selected]));
    }
}

Population::~Population() = default;

void Population::replicate() {
//printf("in replicate\n");
    int num_genomes = genomes.size();
    for (int i = 0; i < num_genomes; i++) {
        genomes.push_back(Genome(genomes[i]));
    }
}

void Population::mutate() {
//printf("in mutate\n");
    // calculate number of mutations this generation
    float mutations_expected = (mutation_rate * genome_size * genomes.size());
    int rounded_mutations_expected = (int) round(mutations_expected);
    int poisson_mutations = poisson_dist(rounded_mutations_expected, random_seed);
    // select genomes to be mutated
    int selected_genome;
    for (int i = 0; i < poisson_mutations; i++) {
        selected_genome = uniform_random_in_range(genomes.size(), random_seed);
        genomes[selected_genome].add_random_mutation(genome_size);
    }
}

void Population::select() {
//printf("in select\n");
    int selected;
    while (genomes.size() > carrying_capacity) {
        selected = uniform_random_in_range(genomes.size(), random_seed);
        genomes[selected] = genomes.back();
        genomes.pop_back();
    }
}

void Population::evolve() {
    for (int i = 0; i < generations; i++) {
        if (i % 500 == 0) {
            printf("generation %d\n", i);
        }
        replicate();
        mutate();
        select();
    }
}


