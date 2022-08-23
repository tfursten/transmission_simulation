#include "sample.hpp"
#include "../utils.hpp"

using std::vector;

Sample::Sample(Population &pop, int size) {
    int selected;
    for (int i = 0; i < size; i++) {
        selected = uniform_random_in_range(pop.genomes.size(), random_seed);
        genomes.push_back(Genome(pop.genomes[selected]));
    }

    get_snps();
    find_snp_proportions();
}

void Sample::get_snps() {
    for (int i = 0; i < genomes.size(); i++) {
        vector<int> mutations = genomes[i].mutations;

        for (int j = 0; j < mutations.size(); j++) {
            if (snps.count(mutations[j]) == 0) {
                snps[mutations[j]] = Snp {
                    .count = 1,
                    .proportion = 0,
                };
            }
            else {
                snps[mutations[j]].count++;
            }
        }
    }
}

void Sample::find_snp_proportions() {
    for (auto &pair : snps) {
        pair.second.proportion = (float) pair.second.count / genomes.size();
    }
}