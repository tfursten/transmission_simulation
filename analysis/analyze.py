from dataclasses import dataclass
import sys
import os
import glob
import json
from statistics import mean
import logging
logging.getLogger().setLevel(logging.INFO)

from Analysis import Analysis


# python analyze.py run_params.json analysis_params.json population_files_dir
if __name__ == "__main__":
  run_params_file = sys.argv[1]
  analysis_params_file = sys.argv[2]
  pop_files_dir = sys.argv[3]

  run_params = {}
  analysis_params = {}
  with open(run_params_file, "r") as file:
    run_params = json.load(file)
  with open(analysis_params_file, 'r') as file:
    analysis_params = json.load(file)

  # find all population files belonging to simulation
  run_id = run_params["run_id"]
  pop_files_pattern = \
    os.path.join(pop_files_dir, "run_" + str(run_id) + "*pop*csv")
  pop_files = glob.glob(pop_files_pattern)
  source_pop_files = [file for file in pop_files if "source" in file]
  recipient_pop_files = [file for file in pop_files if "recipient" in file]

  # ensure files from matching simulation runs are analyzed together
  source_pop_files.sort()
  recipient_pop_files.sort()

  # perform analyses
  simulation_outputs = []
  sim_count = 1
  for source_pop, recipient_pop in zip(source_pop_files, recipient_pop_files):
    logging.info("simulation repetition: {}".format(sim_count))
    sim_count += 1
    for i in range(analysis_params["analysis repetitions"]):
      logging.info("\tanalysis repetition: {}".format(i + 1))
      analysis_params["source population file"] = source_pop
      analysis_params["recipient population file"] = recipient_pop
      analysis = Analysis.from_params(analysis_params)
      analysis.perform_analysis()
      simulation_outputs.append(analysis.get_output())

  # long form json output
  output = {}
  for simulation_output in simulation_outputs:
    simulation_output.update(run_params)
    simulation_output.update(analysis_params)
  
  print(json.dumps(simulation_outputs))