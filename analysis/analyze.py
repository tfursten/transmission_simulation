from dataclasses import dataclass
import sys
import os
import glob
import json
from statistics import mean
import logging
logging.getLogger().setLevel(logging.INFO)

from Analysis import Analysis


@dataclass
class AnalysisParams:
  def __init__(self, run_id, analysis_repetitions, sample_size, 
               combination_size, num_clumpiness_bins, 
               source_population_file=None, recipient_population_file=None):
    self.run_id = run_id
    self.analysis_repetitions = analysis_repetitions
    self.sample_size = sample_size
    self.combination_size = combination_size
    self.num_clumpiness_bins = num_clumpiness_bins
    self.source_population_file = source_population_file
    self.recipient_population_file = recipient_population_file

def parse_analysis_params(analysis_params_file):
  analysis_params_dict = {}
  with open(analysis_params_file, 'r') as file:
    analysis_params_dict = json.load(file)
  
  return AnalysisParams(
    run_id=analysis_params_dict["run id"],
    analysis_repetitions=analysis_params_dict["analysis repetitions"],
    sample_size=analysis_params_dict["sample size"],
    combination_size=analysis_params_dict["combination size"],
    num_clumpiness_bins=analysis_params_dict["number clumpiness bins"],
  )

def analyze(analysis_params):
  analysis_repetitions = []
  for _ in range(analysis_params.analysis_repetitions):
    logging.info(
      "\tanalysis repetition: {}".format(len(analysis_repetitions) + 1)
    )
    analysis = Analysis.from_params(analysis_params)
    analysis.perform_analysis()
    analysis.calculate_output()
    analysis_repetitions.append(analysis.get_output())

  return average_repetitions(analysis_repetitions)

def average_repetitions(repetitions):
  average_output = repetitions[0].copy()
  for key in repetitions[0]:
    average_output[key] = round(mean([r[key] for r in repetitions]), 4)

  return average_output


# python analyze.py analysis_params.json population_files_dir
if __name__ == "__main__":
  # parse analysis params from json file
  analysis_params = parse_analysis_params(sys.argv[1])

  # find all population files belonging to simulation
  run_id = analysis_params.run_id
  pop_files_dir = sys.argv[2]
  pop_files_pattern = \
    os.path.join(pop_files_dir, "run_" + str(run_id) + "*pop*csv")
  pop_files = glob.glob(pop_files_pattern)
  source_pop_files = [file for file in pop_files if "source" in file]
  recipient_pop_files = [file for file in pop_files if "recipient" in file]

  # ensure files from matching simulation runs are analyzed together
  source_pop_files.sort()
  recipient_pop_files.sort()

  # perform analyses
  simulation_repetitions = []
  for source_pop, recipient_pop in zip(source_pop_files, recipient_pop_files):
    logging.info(
      "simulation repetition: {}".format(len(simulation_repetitions) + 1)
    )
    analysis_params.source_population_file = source_pop
    analysis_params.recipient_population_file = recipient_pop
    simulation_repetitions.append(analyze(analysis_params))

  results = average_repetitions(simulation_repetitions)

  # get simulation parameters
  # assumes parameters file in same dir as population files
  run_params_file = \
    os.path.join(pop_files_dir, "run_id_" + str(run_id) + ".json") 
  run_params = {}
  with open(run_params_file, "r") as file:
    run_params = json.load(file)

  run_params.update({
    "sample size": analysis_params.sample_size,
    "combo size": analysis_params.combination_size,
    "number of clumpiness bins": analysis_params.num_clumpiness_bins,
    "analyses": results["analyses"],
    "trees": results["trees"],
  })
  run_params.update(results)
  print(json.dumps(output := run_params))

  