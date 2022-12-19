#include <stdlib.h>
#include <math.h>
#include <assert.h>
#include <time.h>
#include <string>
#include <iostream>
#include <fstream>

#include <boost/iostreams/filtering_streambuf.hpp>
#include <boost/iostreams/copy.hpp>
#include <boost/iostreams/filter/gzip.hpp>

#include <vector>
using std::vector;

#include "utils.hpp"


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


void combinations(int offset, int k, const vector<int> &in, 
                                                     vector<vector<int>> &out) {
    static vector<int> combs;

    if (k == 0) {
        vector<int> temp;
        for (int i = 0; i < combs.size(); i++) {
            temp.push_back(combs[i]);
        }
        out.push_back(temp);
        return;
    }

    for (int i = offset; i <= in.size() - k; ++i) {
        combs.push_back(in[i]);
        combinations(i+1, k-1, in, out);
        combs.pop_back();
    }
}


void read_gzip_file(std::string compressed_file, 
                    std::string decompressed_file) {

    using namespace std;
    using namespace boost::iostreams;

    ifstream file(compressed_file, ios_base::in | ios_base::binary);
    filtering_streambuf<input> in;
    in.push(gzip_decompressor());
    in.push(file);
    
    ofstream outfile;
    outfile.open(decompressed_file);
    boost::iostreams::copy(in, outfile);
    outfile.close();
}

void write_gzip_file(std::string input_file, std::string compressed_file) {
    using namespace std;
    using namespace boost::iostreams;

    ifstream file(input_file);
    filtering_streambuf<input> in;
    in.push(gzip_compressor());
    in.push(file);
    
    ofstream outfile;
    outfile.open(compressed_file);
    boost::iostreams::copy(in, outfile);
    outfile.close();

    const char* old_file = input_file.c_str();
    remove(old_file);
}

int main() {

    return 0;
}