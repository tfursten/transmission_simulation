#ifndef TRANSMISSION_HPP
#define TRANSMISSION_HPP

#include "sample.hpp"

#include <vector>
using std::vector;


typedef struct Stats {
    int carrying_capacity;
    int sample_size;
    int src_generations;
    int rec_generations;
    int bottleneck;
    float tier_1_fraction;
    float tier_2_fraction;
    vector<int> ancestral_branch_segs;

} Stats;

class Transmission {
    private:
        vector<int> get_shared_snps(Genome first, Genome second);
        vector<int> get_unique_snps(Genome first, Genome second);
        int count_segragating_snps(Sample sample, vector<int> snps);

    public:
        Transmission(Population *src, Population *rec, int size);
        Sample src;
        Sample rec;
        Stats stats;
        void analyze_tier1();
        void analyze_tier2();
        void write_results(int repetition);

};


#endif