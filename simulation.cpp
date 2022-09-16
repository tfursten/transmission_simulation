#include <stdlib.h>
#include <cmath>
#include <fstream>
#include <iostream>

#include "json.hpp"
using nlohmann::json;

#include "simulation.hpp"
#include "population/population.hpp"
#include "population/sample.hpp"
#include "population/genome.hpp"
#include "population/transmission.hpp"
#include "utils.hpp"

#include <vector>
using std::vector;
using std::string;

int random_seed;

int main(int argv, char** argc) {

    // ./run [json params file] [(optional) random seed] [(optional) repetition] 

    std::ifstream  params_file(argc[1]);
    json params = json::parse(params_file);

    int run_id = params["run_id"];
    double mu = params["mutation rate"];
    int genome_size = params["genome size"];
    int carrying_capacity = params["carrying capacity"];
    int src_gens = params["source generations"];
    int bottleneck = params["bottleneck"];
    int rec_gens = params["recipient generations"];
    int sample_size = params["sample size"];
    vector<int> combo_sizes = params["combo sizes"];

    random_seed = 1;
    if (argv > 2) {
        random_seed = atoi(argc[2]);
    }
    int repetition = 0;
    if (argv > 3) {
        repetition = atoi(argc[3]);
    }
    

    // simulation

        // evolution in source
        Population source(mu, carrying_capacity, src_gens, rec_gens, genome_size);
        source.evolve(src_gens);

        // transmission event
        Population recipient(source, bottleneck, rec_gens);

        // evolution post transmission
        recipient.evolve(rec_gens);
        source.evolve(rec_gens);

        // transmission analysis
        Transmission trans(source, recipient, sample_size);
        trans.analyze(combo_sizes, 200);
        trans.write_results(run_id, repetition); 
}

