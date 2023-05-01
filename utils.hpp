#ifndef UTILS_HPP
#define UTILS_HPP

#include <vector>
#include <string>

int poisson_dist(int expected, int seed);
int uniform_random_in_range(int limit, int seed);
void write_gzip_file(std::string input_file, std::string compressed_file);

#endif