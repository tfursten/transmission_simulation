#ifndef UTILS_HPP
#define UTILS_HPP

#include <vector>

int poisson_dist(int expected, int seed);
int uniform_random_in_range(int limit, int seed);
void combinations(int offset, int k, const std::vector<int> &in, 
                                            std::vector<std::vector<int>> &out);


#endif