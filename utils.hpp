#ifndef UTILS_HPP
#define UTILS_HPP

#include <vector>
#include <string>

int poisson_dist(int expected, int seed);
int uniform_random_in_range(int limit, int seed);
void combinations(int offset, int k, const std::vector<int> &in, 
                                            std::vector<std::vector<int>> &out);
void read_gzip_file(std::string compressed_file, std::string decompressed_file);
void write_gzip_file(std::string input_file, std::string compressed_file);

#endif