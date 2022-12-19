#include <vector>
#include <stdio.h>
#include <cmath>
#include <fstream>
#include <iostream>
#include <string>


#include "population.hpp"
#include "genome.hpp"
#include "../utils.hpp"

using std::vector;


vector<Genome*> init_population() {
    vector<Genome*> population;
    Genome* founder = new Genome;
    population.push_back(founder);
    return population;
}


void replicate_population(vector<Genome*> &population) {
    int initial_size = population.size();
    for (int i = 0; i < initial_size; i++) {
        population.push_back(copy_genome(population[i]));
    }
}

void mutate_population(vector<Genome*> &population, double mutation_rate,
                       int genome_length) {

    // calculate number of mutations expected this generation
    float mutations_expected = (mutation_rate * genome_length * 
                                population.size());
    int rounded_mutations_expected = (int) round(mutations_expected);
    int poisson_mutations = poisson_dist(rounded_mutations_expected, 
                                         random_seed);
    
    // select and mutate genomes
    int selected_genome;
    for (int i = 0; i < poisson_mutations; i++) {
        selected_genome = uniform_random_in_range(population.size(), 
                                                  random_seed);
        add_random_mutation(population[selected_genome], genome_length);
    }
}

void select_population(vector<Genome*> &population, int carrying_capacity) {
    int selected;
    while (population.size() > carrying_capacity) {
        selected = uniform_random_in_range(population.size(), random_seed);
        delete population[selected];
        population[selected] = population[population.size() - 1];
        population.pop_back();
    }
}

void evolve_population(vector<Genome*> &population, 
                       SimulationParameters params, int generations) {

    for (int i = 0; i < generations; i++) {
        if (i % 500 == 0) {
            printf("generation %d\n", i);
        }
        replicate_population(population);
        mutate_population(population, params.mutation_rate, 
                          params.genome_length);
        select_population(population, params.carrying_capacity);
    }
}

void transmit(vector<Genome*> &source_population, 
                          vector<Genome*> &recipient_population, 
                          int bottleneck) {

    int selected_genome;
    for (int i = 0; i < bottleneck; i++) {
        selected_genome = uniform_random_in_range(source_population.size(), 
                                                  random_seed);
        recipient_population.push_back(
            copy_genome(source_population[selected_genome]));
    }
}

void population_to_file(vector<Genome*> &population, std::string output_file) {

    std::ofstream file;

    file.open(output_file);
    for (Genome* genome : population) {
        for (int mutation : genome->mutations) {
            file << mutation << ',';
        }
        file << '\n';
    }
    file.close();
}
