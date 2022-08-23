#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include <assert.h>

#include <vector>
#include <map>
#include <algorithm>
using std::vector;
using std::map;










int main() {
    
    vector<int> in {1,3,5};
    vector<vector<int>> out;
    combinations(0, 1, in, out);
	
    for (int i = 0; i < out.size(); i++) {
        printf("combination %d: ", i);
        for (int j = 0; j < out[i].size(); j++) {
            printf("%d, ", out[i][j]);
        }
        printf("\n");
    }

	return 0;
}
