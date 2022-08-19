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
                                              int generations, int genome_size);
        Population(const Population &source, int bottleneck, int generations);
        ~Population();

        vector<Genome> genomes;
        double mutation_rate;
        int carrying_capacity;
        int generations;
        int genome_size;
        int bottleneck;
        
        void replicate();
        void mutate();
        void select();
        void evolve();

};


#endif