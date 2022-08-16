#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include <assert.h>

#include <vector>
#include <map>
using std::vector;
using std::map;

int main() {

	vector<int> v{1,2,3,4,5};

    map<int, int> m { {1, 99}, {3, 70} };


    if (v.find(3) == v.end()) {
        printf("not found\n");
    }

	return 0;
}
