#include <stdlib.h>
#include <stdio.h>
#include <cmath>

#include "simulation.hpp"
#include "population.hpp"
#include "utils.h"

#include <vector>
using std::vector;



int main(int argv, char** argc) {

    // ./run [carrying capacity] [src gens] [bottleneck] [rec gens] [sample size]

    double mu = 1.6 * pow(10, -10);
    int carrying_capacity = atoi(argc[1]);
    int src_gens = atoi(argc[2]);
    int bottleneck = atoi(argc[3]);
    int rec_gens = atoi(argc[4]);
    int sample_size = atoi(argc[5]);
    int repetition = 0;
    if (argv == 7) {
        repetition = atoi(argc[6]);
    }
    int genome_size = 2800000;

    Population source(mu, carrying_capacity, src_gens, genome_size);
    source.evolve();

    Population recipient(source, bottleneck, rec_gens);
    recipient.evolve();


    Transmission trans(&source, &recipient, sample_size);
    trans.analyze_tier1();
    trans.analyze_tier2();
    trans.write_results(repetition);
    
}

