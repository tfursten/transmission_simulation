#ifndef POPULATION_HPP
#define POPULATION_HPP

#include <vector>
using std::vector;

#include "genome.hpp"

extern int random_seed;

class Population {
    private:

    public:
        Population(double mutation_rate, int carrying_capacity, 
                     int src_generations, int rec_generations, int genome_size);
        Population(const Population &source, int bottleneck, 
                                                           int rec_generations);
        ~Population();

        vector<Genome> genomes;
        double mutation_rate;
        int carrying_capacity;
        int src_generations;
        int rec_generations;
        int genome_size;
        int bottleneck;
        
        void replicate();
        void mutate();
        void select();
        void evolve(int generations);

};


#endif