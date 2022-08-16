#include <vector>
#include <algorithm>
#include <iostream>
#include <fstream>

#include <math.h>
#include <cmath>
#include <stdio.h>

#include "population.hpp"
#include "utils.h"

using std::vector;

// population
Population::Population(double mutation_rate, int carrying_capacity, 
                                             int generations, int genome_size) {
    Population::mutation_rate = mutation_rate;
    Population::carrying_capacity = carrying_capacity;
    Population::generations = generations;
    Population::genome_size = genome_size;

    Genome founder;
    genomes.push_back(founder);
}

Population::Population(const Population &source, int bottleneck, 
                                                              int generations) {
    Population::mutation_rate = source.mutation_rate;
    Population::carrying_capacity = source.carrying_capacity;
    Population::genome_size = source.genome_size;
    Population::generations = generations;
    Population::bottleneck = bottleneck;
    
    int selected;
    for (int i = 0; i < bottleneck; i++) {
        selected = uniform_random_in_range(source.genomes.size());
        genomes.push_back(Genome(source.genomes[selected]));
    }
}

Population::~Population() {}

void Population::replicate() {
//printf("in replicate\n");
    int num_genomes = genomes.size();
    for (int i = 0; i < num_genomes; i++) {
        genomes.push_back(Genome(genomes[i]));
    }
}

void Population::mutate() {
//printf("in mutate\n");
    // calculate number of mutations this generation
    float mutations_expected = (mutation_rate * genome_size * genomes.size());
    int rounded_mutations_expected = (int) round(mutations_expected);
    int poisson_mutations = poisson_dist(rounded_mutations_expected);
    // select genomes to be mutated
    int selected_genome;
    for (int i = 0; i < poisson_mutations; i++) {
        selected_genome = uniform_random_in_range(genomes.size());
        genomes[selected_genome].add_random_mutation(genome_size);
    }
}

void Population::select() {
//printf("in select\n");
    int selected;
    while (genomes.size() > carrying_capacity) {
        selected = uniform_random_in_range(genomes.size());
        genomes[selected] = genomes.back();
        genomes.pop_back();
    }
}

void Population::evolve() {
    for (int i = 0; i < generations; i++) {
        if (i % 500 == 0) {
            printf("generation %d\n", i);
        }
        replicate();
        mutate();
        select();
    }
}


// genome
Genome::Genome() {}
Genome::Genome(const Genome &copied) {
    mutations = copied.mutations;
}

void Genome::add_random_mutation(int genome_size) {
    int random_mutation = uniform_random_in_range(genome_size + 1);
    mutations.push_back(random_mutation);
}

vector<int> Genome::get_mutations() {
    return mutations;
}


// sample
Sample::Sample(Population *pop, int size) {
    Sample::size = size;
    int selected;
    for (int i = 0; i < size; i++) {
        selected = uniform_random_in_range(pop->genomes.size());
        sample.push_back(Genome(pop->genomes[selected]));
    }

    get_snps();
    get_segregating_snps();
}

void Sample::get_snps() {
    for (int i = 0; i < sample.size(); i++) {
        vector<int> mutations = sample[i].get_mutations();

        for (int j = 0; j < mutations.size(); j++) {
            if (snps.count(mutations[j]) == 0) {
                snps[mutations[j]] = Snp {
                    .position = mutations[j],
                    .count = 1,
                    .proportion = -1,
                };
            }
            else {
                snps[mutations[j]].count++;
            }
        }
    }
}

void Sample::get_segregating_snps() {
    for (auto const &pair : snps) {
        snps[pair.first].proportion = (float) pair.second.count / size;
    }
}


// transmission
Transmission::Transmission(Population *src_pop, Population *rec_pop, int size)
                                      : src(src_pop, size), rec(rec_pop, size) {
    Transmission::stats.carrying_capacity = src_pop->carrying_capacity;
    Transmission::stats.src_generations = src_pop->generations;
    Transmission::stats.rec_generations = rec_pop->generations;
    Transmission::stats.sample_size = size;
    Transmission::stats.bottleneck = rec_pop->bottleneck;


}

void Transmission::analyze_tier1() {
    vector<int> shared_snps;
    int src_segregating, rec_segregating;
    int combo_counter = 0, src_more_seg_counter = 0;
    for (int i = 0; i < src.sample.size(); i++) {
        for (int j = 0; j < rec.sample.size(); j++) {
            shared_snps = get_shared_snps(src.sample[i], rec.sample[j]);
            src_segregating = count_segragating_snps(src, shared_snps);
            rec_segregating = count_segragating_snps(rec, shared_snps);

            if (src_segregating > rec_segregating) {
                src_more_seg_counter++;
            }
            combo_counter++;
        }
    }

    stats.tier_1_fraction = (float) src_more_seg_counter / combo_counter;
}

void Transmission::analyze_tier2() {
    vector<int> src_branch;
    vector<int> rec_branch;
    int src_on_rec_segregating, rec_on_src_segregating;
    int combo_counter = 0, tier_2_met_counter = 0;
    for (int i = 0; i < src.sample.size(); i++) {
        for (int j = 0; j < rec.sample.size(); j++) {
            src_branch = get_unique_snps(src.sample[i], rec.sample[j]);
            rec_branch = get_unique_snps(rec.sample[j], src.sample[i]);
            src_on_rec_segregating = count_segragating_snps(src, rec_branch);
            rec_on_src_segregating = count_segragating_snps(rec, src_branch);

            if (src_on_rec_segregating > 0 && rec_on_src_segregating == 0) {
                tier_2_met_counter++;
            }
            combo_counter++;
        }
    }

    stats.tier_2_fraction = (float) tier_2_met_counter / combo_counter;
}

vector<int> Transmission::get_shared_snps(Genome first, Genome second) {
    vector<int> first_snps = first.get_mutations();
    vector<int> second_snps = second.get_mutations();

    vector<int> shared_snps;
    for (int i = 0; i < first_snps.size(); i++) {
        if (std::find(second_snps.begin(), second_snps.end(), first_snps[i]) 
                                                         != second_snps.end()) {
            shared_snps.push_back(first_snps[i]);
        }
    }
    return shared_snps;
}

vector<int> Transmission::get_unique_snps(Genome first, Genome second) {
    vector<int> first_snps = first.get_mutations();
    vector<int> second_snps = second.get_mutations();

    vector<int> unique_snps;
    for (int i = 0; i < first_snps.size(); i++) {
        if (std::find(second_snps.begin(), second_snps.end(), first_snps[i]) 
                                                         == second_snps.end()) {
            unique_snps.push_back(first_snps[i]);
        }
    }

    return unique_snps;
}

int Transmission::count_segragating_snps(Sample sample, vector<int> snps) {
    int count = 0;
    float proportion;
    for (int i = 0; i < snps.size(); i++) {
        if (sample.snps.count(snps[i]) != 0) {
            proportion = sample.snps[snps[i]].proportion;
            if ( proportion < 1 && proportion > 0) {
                count++;
            }
        }
    }
    return count;
}

void Transmission::write_results(const char *filename) {
    std::ofstream file;
    file.open(filename);
    using std::endl;
    file << "carrying capacity: " << stats.carrying_capacity << endl;
    file << "sample size: " << stats.sample_size << endl;
    file << "src_generations: " << stats.src_generations << endl;
    file << "rec_generations: " << stats.rec_generations << endl;
    file << "bottleneck: " << stats.bottleneck << endl;
    file << "tier 1 fraction: " << stats.tier_1_fraction << endl;
    file << "tier 2 fraction: " << stats.tier_2_fraction << endl;

    file.close();
}



