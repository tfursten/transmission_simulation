#include <vector>
#include <iostream>
#include <fstream>
#include <algorithm>
#include <numeric>
#include <assert.h>

#include "./../json.hpp"
using nlohmann::json;

#include "transmission.hpp"
#include "../utils.hpp"

using std::vector;

Transmission::Transmission(Population &src_pop, Population &rec_pop, int size)
    : src {src_pop, size}, 
      rec {rec_pop, size}, 
      stats {} {}


void Transmission::analyze(vector<int> combo_sizes, int iterations) {

    for (int combo_size : combo_sizes) {
        int tier1_counter = 0, tier2_counter = 0, combined_counter = 0,
            combined_and_counter = 0;
        
        for (int i = 0; i < iterations; i++) {
            int src_selected, rec_selected;
            int seg_diff = 0;
            int tier_2 = 0;
            for (int j = 0; j < combo_size; j++) {
                src_selected = uniform_random_in_range(src.genomes.size(), 
                                                                   random_seed);
                rec_selected = uniform_random_in_range(rec.genomes.size(), 
                                                                   random_seed);
                // tier 1                                               
                seg_diff += tier1_seg_diff(src.genomes[src_selected], 
                                                     rec.genomes[rec_selected]);
                
                // tier 2
                if (tier2(src.genomes[src_selected], rec.genomes[rec_selected])) 
                {
                    tier_2++;
                }
            }
            if (seg_diff > 0) tier1_counter++;
            if (tier_2 > 0) tier2_counter++;
            if (seg_diff > 0 || tier_2 > 0) combined_counter++;

        }
        stats.tier_1_fractions[combo_size] = (float) tier1_counter / iterations;
        stats.tier_2_fractions[combo_size] = (float) tier2_counter / iterations;
        stats.combined_outcome[combo_size] = (float) combined_counter / 
                                                                     iterations;
    }
}

int Transmission::tier1_seg_diff(const Genome &src_genome, 
                                                     const Genome &rec_genome) {
    int src_segs, rec_segs;
    vector<int> ancestral_branch = get_shared_snps(src_genome, rec_genome);
    src_segs = count_segragating_snps(src, ancestral_branch);
    rec_segs = count_segragating_snps(rec, ancestral_branch);

    return src_segs - rec_segs;
}

bool Transmission::tier2(const Genome &src_genome, const Genome &rec_genome) {
    int src_on_rec_segs, rec_on_src_segs;
    vector<int> src_branch = get_unique_snps(src_genome, rec_genome);
    vector<int> rec_branch = get_unique_snps(rec_genome, src_genome);
    src_on_rec_segs = count_segragating_snps(src, rec_branch);
    rec_on_src_segs = count_segragating_snps(rec, src_branch);

    if (src_on_rec_segs > 0 && rec_on_src_segs == 0) {
        return true;
    }
    return false;
}

vector<int> Transmission::get_shared_snps(const Genome &first, 
                                                         const Genome &second) {
    vector<int> shared_snps;
    for (int i = 0; i < first.mutations.size(); i++) {
        auto position = std::find(second.mutations.begin(), 
                                    second.mutations.end(), first.mutations[i]);
        if ( position != second.mutations.end() ) {
            shared_snps.push_back(first.mutations[i]);
        }
    }
    return shared_snps;
}

vector<int> Transmission::get_unique_snps(const Genome &first, 
                                                         const Genome &second) {
    vector<int> unique_snps;
    for (int i = 0; i < first.mutations.size(); i++) {
        auto position = std::find(second.mutations.begin(), 
                                    second.mutations.end(), first.mutations[i]);
        if ( position == second.mutations.end() ) {
            unique_snps.push_back(first.mutations[i]);
        }
    }
    return unique_snps;
}

int Transmission::count_segragating_snps(Sample sample, 
                                               const vector<int> &subset_snps) {
    int num_segs = 0;
    float proportion;
    for (int i = 0; i < subset_snps.size(); i++) {
        if (sample.snps.count(subset_snps[i]) != 0) {
            proportion = sample.snps[subset_snps[i]].proportion;
            assert(proportion != 0);
            if ( proportion < 1) {
                num_segs++;
            }
        }
    }
    return num_segs;
}


void Transmission::write_results(int run_id, int repetition) {
    using namespace std;

    json run_stats = { 
        {"run_id", run_id},
        {"repetition", repetition},
        {"source sample", {}},
        {"recipient sample", {}},
    };

    // raw snps
    cout << "size of source: " << src.genomes.size() << endl;
    cout << "size of recipient: " << rec.genomes.size() << endl;
    for (int i = 0; i < src.genomes.size(); i++) {
        run_stats["source sample"][to_string(i)] = src.genomes[i].mutations;
    }
    for (int i = 0; i < rec.genomes.size(); i++) {
        run_stats["recipient sample"][to_string(i)] = rec.genomes[i].mutations;
    }

    // combo sizes
    for (auto& [key, value] : stats.tier_1_fractions) {
        run_stats["combo-" + to_string(key)]["tier 1 fraction"] = value;
        run_stats["combo-" + to_string(key)]["tier 2 fraction"] = 
                                                    stats.tier_2_fractions[key];
        run_stats["combo-" + to_string(key)]["combined fraction"] = 
                                                    stats.combined_outcome[key];
    }
   
    string out_directory = "/projects/pearson_lab/trans_simulation/runs/run-" 
                                                + to_string(run_id) + '/';
    out_directory = "./"; // change ..
    string statsfile = out_directory + "run-" + to_string(run_id) 
                                    + "-rep-" + to_string(repetition) + ".json";

    ofstream file;
    file.open(statsfile);
    file << run_stats;
    file.close();
}