#ifndef SAMPLE_HPP
#define SAMPLE_HPP

#include <vector>
#include <map>

#include "genome.hpp"
#include "population.hpp"

extern int random_seed;

typedef struct Snp {
    int count;
    float proportion;
} Snp;

class Sample {
    private:
        void get_snps();
        void find_snp_proportions();

    public:
        Sample(Population &pop, int size);
        std::vector<Genome> genomes;
        std::map<int, Snp> snps;

};


#endif