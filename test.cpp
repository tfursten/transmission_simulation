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

#include "json.hpp"
using nlohmann::json;

#include <iostream>
using std::cout;

#include <fstream>









int main() {

    std::ifstream file("test.json");

    json data = json::parse(file);

    cout << "name: " << data["name"] << "\n";
    cout << "testing: " << data["one two"] << "\n";

	return 0;
}
