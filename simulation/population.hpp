#ifndef POPULATION_HPP
#define POPULATION_HPP

#include <vector>
#include <string>

#include "genome.hpp"

extern int random_seed;


struct SimulationParameters {
    int run_id;
    int repetition;
    double mutation_rate;
    int genome_length;
    int carrying_capacity;
    int source_generations;
    int recipient_generations;
    int bottleneck;
    std::string output_path;
};

std::vector<Genome*> init_population();

void replicate_population(std::vector<Genome*> &population);
void mutate_population(std::vector<Genome*> &population, double mutation_rate, 
                       int genome_length);
void select_population(std::vector<Genome*> &population, 
                       int carrying_capacity);
void evolve_population(std::vector<Genome*> &population, 
                       SimulationParameters params, int generations);

void transmit(std::vector<Genome*> &source_population, 
              std::vector<Genome*> &recipient_population, int bottleneck);

void population_to_file(std::vector<Genome*> &population, 
                        std::string output_file);

void read_gzip_file(std::string compressed_file, std::string decompressed_file);
void write_gzip_file(std::string input_file, std::string compressed_file);

#endif