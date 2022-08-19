#include "sample.hpp"
#include "../utils.h"

using std::vector;

Sample::Sample(Population *pop, int size) {
    Sample::size = size;
    int selected;
    for (int i = 0; i < size; i++) {
        selected = uniform_random_in_range(pop->genomes.size(), random_seed);
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