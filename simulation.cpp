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
    double mu = stod( params["mutation rate"].get<string>() );
    int genome_size = stoi( params["genome size"].get<string>() );
    int carrying_capacity = stoi( params["carrying capacity"].get<string>() );
    int src_gens = stoi( params["source generations"].get<string>() );
    int bottleneck = stoi( params["bottleneck"].get<string>() );
    int rec_gens = stoi( params["recipient generations"].get<string>() );
    int sample_size = stoi( params["sample size"].get<string>() );

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
        trans.analyze(std::vector<int>{1,2,3}, 200);
        trans.write_results(repetition); 
}

