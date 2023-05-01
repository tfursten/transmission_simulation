#include <ctime>
#include <cmath>
#include <vector>
#include <cassert>
#include <iostream>

#include "tests.hpp"
#include "utils.hpp"
#include "simulation/genome.hpp"
#include "simulation/population.hpp"


using std::cout;
using std::endl;
using std::vector;

int random_seed = time(NULL);

int main() {
    test_uniform_random_in_range();
    test_poisson_dist();
    test_add_random_mutation();
    test_copy_genome();
    test_init_population();
    test_replicate_population();
    test_mutate_population();
    test_select_population();
    test_transmit();
}


void test_poisson_dist() {
    int actual;
    for (int i = 0; i < 100; i++) {
        actual = poisson_dist(10, random_seed * i);
        assert(actual < 25 && "small random chance of failure, rerun");
        assert(actual >= 0);
    }
}
void test_uniform_random_in_range() {
    int actual;
    for (int i = 0; i < 100; i++) {
        actual = uniform_random_in_range(10, time(NULL) * i);
        assert(actual < 10);
        assert(actual >= 0);
    }
}

void test_add_random_mutation() {
    Genome* genome = new Genome;
    for (int i = 0; i < 5; i++) {
        add_random_mutation(genome, 1000);
    }
    assert(genome->mutations.size() == 5);

    int mutation;
    for (int i = 0; i < 5; i++) {
        mutation = genome->mutations[i];
        for (int j = 0; j < 5; j++) {
            if (i == j) continue;
            assert(mutation != genome->mutations[j] 
                   && "small random chance of failure, rerun");
        }
    }
}
void test_copy_genome() {
    Genome* genome = new Genome;
    for (int i = 0; i < 10; i++) {
        add_random_mutation(genome, 100);
    }

    Genome* copied_genome = copy_genome(genome);
    for (int i = 0; i < 10; i++) {
        assert(genome->mutations[i] == copied_genome->mutations[i]);
    }
}

void test_init_population() {
    vector<Genome*> pop = init_population();
    assert(pop.size() == 1);
    assert(pop[0]->mutations.size() == 0);
}
void test_replicate_population() {
    vector<Genome*> pop = init_population();
    for (int i = 0; i < 10; i++) {
        assert(pop.size() == std::pow(2, i));
        replicate_population(pop);
    } 
}
void test_mutate_population() {
    vector<Genome*> pop = init_population();
    for (int i = 0; i < 10; i++) {
        replicate_population(pop);
    } 
    int previous_mutation_count = count_mutations_in_population(&pop);
    int current_mutation_count;
    for (int i = 0; i < 10; i++) {
        mutate_population(pop, 0.01, 100);
        current_mutation_count = count_mutations_in_population(&pop);
        assert(current_mutation_count > previous_mutation_count
               && "small random chance of failure, rerun");
        
        previous_mutation_count = current_mutation_count;
    }
}
void test_select_population() {
    vector<Genome*> pop = init_population();
    for (int i = 0; i < 10; i++) {
        replicate_population(pop);
    } 
    select_population(pop, 50);
    assert(pop.size() == 50);
    select_population(pop, 3);
    assert(pop.size() == 3);
}
void test_transmit() {
    vector<Genome*> src_pop = init_population();
    for (int i = 0; i < 10; i++) {
        replicate_population(src_pop);
    } 

    vector<Genome*> rec_pop;
    transmit(src_pop, rec_pop, std::pow(2, 9));
    assert(rec_pop.size() == std::pow(2, 9));

    vector<Genome*> rec_pop_bottleneck;
    transmit(src_pop, rec_pop_bottleneck, 42);
    assert(rec_pop_bottleneck.size() == 42);
}


// helpers
int count_mutations_in_population(vector<Genome*>* population) {
    int count = 0;
    for (int i = 0; i < population->size(); i++) {
        count += population->at(i)->mutations.size();
    }
    return count;
}

