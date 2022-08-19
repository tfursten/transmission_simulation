#include <vector>
#include <iostream>
#include <fstream>
#include <algorithm>
#include <numeric>

#include "transmission.hpp"

using std::vector;


// transmission
Transmission::Transmission(Population *src_pop, Population *rec_pop, int size)
                                      : src(src_pop, size), rec(rec_pop, size) {
    this->stats.carrying_capacity = src_pop->carrying_capacity;
    this->stats.src_generations = src_pop->generations;
    this->stats.rec_generations = rec_pop->generations;
    this->stats.sample_size = size;
    this->stats.bottleneck = rec_pop->bottleneck;


}

void Transmission::analyze_tier1() {
    vector<int> shared_snps;
    int src_segregating, rec_segregating;
    int combo_counter = 0, src_more_seg_counter = 0;
    int segregating_diff;
    for (int i = 0; i < src.sample.size(); i++) {
        for (int j = 0; j < rec.sample.size(); j++) {
            shared_snps = get_shared_snps(src.sample[i], rec.sample[j]);
            src_segregating = count_segragating_snps(src, shared_snps);
            rec_segregating = count_segragating_snps(rec, shared_snps);

            if (src_segregating > rec_segregating) {
                src_more_seg_counter++;
            }
            combo_counter++;

            segregating_diff = src_segregating - rec_segregating;
            stats.ancestral_branch_segs.push_back(segregating_diff);
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


void Transmission::write_results(int repetition) {
    using namespace std;
    string statsfile = "stats-srcgen-" + to_string(stats.src_generations) 
                                     + "-rep-" + to_string(repetition) + ".txt";

    ofstream file;
    file.open(statsfile);
    file << "carrying capacity: " << stats.carrying_capacity << endl;
    file << "sample size: " << stats.sample_size << endl;
    file << "src_generations: " << stats.src_generations << endl;
    file << "rec_generations: " << stats.rec_generations << endl;
    file << "bottleneck: " << stats.bottleneck << endl;
    file << "tier 1 fraction: " << stats.tier_1_fraction << endl;
    file << "tier 2 fraction: " << stats.tier_2_fraction << endl;

    vector<int> a = stats.ancestral_branch_segs;
    float average = accumulate(a.begin(), a.end(), 0.0) / a.size();
    file << "average ancestral branch diff: " << average << endl;
    file.close();

    string segs_file = "segs-srcgen-" + to_string(stats.src_generations) 
                                     + "-rep-" + to_string(repetition) + ".txt";
    file.open(segs_file);
    for (int seg_diff : stats.ancestral_branch_segs) {
        file << seg_diff << ',';
    }
    file << endl;
    file.close();
}