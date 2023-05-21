import os
import sys


# assumes run parameters file and population files in same directory
# assumes analysis_params.json is in current working directory
# python run_many.py pop_files_dir id...
if __name__ == "__main__":
	pop_id_files_dir = sys.argv[1]
	for id in sys.argv[2:]:
		run_id_file = os.path.join(pop_id_files_dir, f"run_id_{id}.json")
		command = f"python analyze.py {run_id_file} analysis_params.json " + \
							f"{pop_id_files_dir} > run_{id}_output.json"
		
		os.system(command)
