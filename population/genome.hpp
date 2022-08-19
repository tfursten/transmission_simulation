#ifndef GENOME_HPP
#define GENOME_HPP

#include <vector>

class Genome {
    private:
        std::vector<int> mutations;
        int random_seed;

    public:
        Genome();
        Genome(const Genome &genome);
        void add_random_mutation(int genome_size);
        std::vector<int> get_mutations();     
};


#endif