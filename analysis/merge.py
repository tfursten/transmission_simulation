import sys
import json


# python merge.py file... 
if __name__ == "__main__":
    files = sys.argv[1:]
    output = []
    for file in files:
      with open(file, 'r') as f:
        output += [*json.load(f)]

    print(json.dumps(output))