#include <stdlib.h>
#include <stdio.h>
#include <cmath>

#include "simulation.hpp"
#include "population/population.hpp"
#include "population/sample.hpp"
#include "population/genome.hpp"
#include "population/transmission.hpp"
#include "utils.h"

#include <vector>
using std::vector;

int random_seed;

int main(int argv, char** argc) {

    // ./run [carrying capacity] [src gens] [bottleneck] [rec gens] 
    //       [sample size] [(optional) random] [(optional) repetition] 

    double mu = 1.6 * pow(10, -10);
    int carrying_capacity = atoi(argc[1]);
    int src_gens = atoi(argc[2]);
    int bottleneck = atoi(argc[3]);
    int rec_gens = atoi(argc[4]);
    int sample_size = atoi(argc[5]);
    random_seed = 1;
    if (argv > 6) {
        random_seed = atoi(argc[6]);
    }
    int repetition = 0;
    if (argv > 7100) {
        repetition = atoi(argc[7]);
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

