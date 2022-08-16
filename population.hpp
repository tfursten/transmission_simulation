#ifndef POPULATION_HPP
#define POPULATION_HPP

#include <vector>
#include <map>
using std::vector;
using std::map;


class Genome {
    private:
        vector<int> mutations;

    public:
        Genome();
        Genome(const Genome &genome);
        void add_random_mutation(int genome_size);
        vector<int> get_mutations();     
};

class Population {
    private:

    public:
        Population(double mutation_rate, int carrying_capacity, 
                                              int generations, int genome_size);
        Population(const Population &source, int bottleneck, int generations);
        ~Population();

        vector<Genome> genomes;
        double mutation_rate;
        int carrying_capacity;
        int generations;
        int genome_size;
        int bottleneck;
        
        void replicate();
        void mutate();
        void select();
        void evolve();

};

typedef struct Snp {
    int position;
    int count;
    float proportion;
} Snp;

class Sample {
    private:
        void get_snps();
        void get_segregating_snps();

    public:
        Sample(Population *pop, int size);
        int size;
        vector<Genome> sample;
        map<int, Snp> snps;

};

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