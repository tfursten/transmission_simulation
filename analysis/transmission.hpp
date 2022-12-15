#ifndef TRANSMISSION_HPP
#define TRANSMISSION_HPP

#include "sample.hpp"

#include <vector>

extern int random_seed;

typedef struct Stats {
    std::map<int, float> tier_1_fractions; 
    std::map<int, float> tier_2_fractions; 
    std::map<int, float> combined_outcome;
} Stats;

class Transmission {
    private:
        vector<int> get_shared_snps(const Genome &first, const Genome &second);
        vector<int> get_unique_snps(const Genome &first, const Genome &second);
        int count_segragating_snps(Sample sample, const std::vector<int> &snps);

    public:
        Transmission(Population &src, Population &rec, int size);
        Sample src;
        Sample rec;
        Stats stats;
        void analyze(std::vector<int> combo_sizes, int iterations);
        int tier1_seg_diff(const Genome &src_genome, const Genome &rec_genome);
        bool tier2(const Genome &src_genome, const Genome &rec_genome);
        void write_results(int run_id, int repetition);

};


#endif