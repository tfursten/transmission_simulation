#include <stdlib.h>
#include <math.h>
#include <assert.h>
#include <time.h>

#include "utils.h"


int poisson_dist(int expected, int seed) {

    static int seeded = 0;
    if (!seeded) {
        srand(seed * time(NULL));
        seeded = 1;
    }

    int remainder = expected;
    int n = 0;
    int step = 600; // avoids under/overflow
    double p = 1;

    do {
        double rand_num = rand() / (double)RAND_MAX;
        p *= rand_num;
        n++;

        while (p < 1 && remainder > 0) {
            if (remainder > step) {
                p *= exp(step);
                remainder = remainder - step;
            } else {
                p *= exp(remainder);
                remainder = 0;
            }
        }
    } while (p > 1);

    return n - 1;
}

// get random number in range [0, limit)
int uniform_random_in_range(int limit, int seed) {

    // seed random number generator
    static int seeded = 0;
    if (!seeded) {
        srand(seed * time(NULL));
        seeded = 1;
    }

    // avoid modulo skew
    int limit_multiples = RAND_MAX / limit;
    int skew_zone_bottom = limit_multiples * limit;
    
    int random_num;
    do {
        random_num = rand();
    } while (random_num > skew_zone_bottom);

    return random_num % limit;
}

