#ifndef GENOME_HPP
#define GENOME_HPP

#include <vector>

extern int random_seed;

class Genome {
    public:
        Genome();
        Genome(const Genome &genome);
        std::vector<int> mutations;
        void add_random_mutation(int genome_size);  
};


#endif