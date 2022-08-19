#ifndef SAMPLE_HPP
#define SAMPLE_HPP

#include <vector>
#include <map>

#include "genome.hpp"
#include "population.hpp"

extern int random_seed;

typedef struct Snp {
    int position;
    int count;
    float proportion;
} Snp;

class Sample {
    private:
        void get_snps();
        void get_segregating_snps();

    public:
        Sample(Population *pop, int size);
        int size;
        std::vector<Genome> sample;
        std::map<int, Snp> snps;

};


#endif