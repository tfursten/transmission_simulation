#include <stdlib.h>
#include <cmath>
#include <fstream>
#include <iostream>

#include "../json.hpp"
using nlohmann::json;

#include "population.hpp"
#include "genome.hpp"
#include "../utils.hpp"

#include <vector>
using std::vector;
using std::string;

using std::cout;
using std::endl;

int random_seed;

int main(int argc, char** argv) {

    // ./run json_params_file [random_seed] [repetition] [output_path] 

    std::ifstream json_params_file(argv[1]);
    json json_params = json::parse(json_params_file);

    SimulationParameters params;

    params.run_id = json_params["run_id"];
    params.mutation_rate = json_params["mutation rate"];
    params.genome_length = json_params["genome size"];
    params.carrying_capacity = json_params["carrying capacity"];
    params.source_generations = json_params["source generations"];
    params.bottleneck = json_params["bottleneck"];
    params.recipient_generations = json_params["recipient generations"];

    if (argc > 2) {
        random_seed = atoi(argv[2]);
    } else {
        random_seed = 1;
    }

    int repetition = 0;
    if (argc > 3) {
        params.repetition = atoi(argv[3]);
    }

    if (argc > 4) {
        params.output_path = argv[4];
    } else {
        params.output_path = ".";
    }

    write_gzip_file("source_pop_rep-0.csv", "source.gz");
    return 0; 
    // simulation

        // evolution in source
        vector<Genome *> source_pop = init_population();
        evolve_population(source_pop, params, params.source_generations);        

        // transmission
        vector<Genome *> recipient_pop;
        transmit(source_pop, recipient_pop, params.bottleneck);

        // evolution post transmission
        evolve_population(source_pop, params, params.recipient_generations);
        evolve_population(recipient_pop, params, params.recipient_generations);

        // write output
        string source_file = params.output_path + "/source_pop_rep-" + 
                             std::to_string(repetition) + ".csv";
        string recipient_file = params.output_path + "/recipient_pop_rep-" +
                                std::to_string(repetition) + ".csv";
        population_to_file(source_pop, source_file);
        population_to_file(recipient_pop, recipient_file);

}

