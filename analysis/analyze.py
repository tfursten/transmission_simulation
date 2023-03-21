import sys
import os
import glob
import json
import logging
logging.getLogger().setLevel(logging.INFO)

from Analysis import Analysis


def average_analysis_outputs(outputs):
  """
  Average the proportions from multiple analysis repetitions into one
  dictionary.
  """
  detections = (
    "correct detection proportion",
    "reverse detection proportion",
    "ambiguous detection proportion"
  )
  accumulator = outputs[0]
  for d in outputs[1:]:
    for key in d:
      for detection in detections:
        accumulator[key][detection] += d[key][detection]

  for key in accumulator:
    for detection in detections:
      accumulator[key][detection] /= len(outputs)

  return accumulator

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
  all_simulation_outputs = []
  sim_count = 1
  for source_pop, recipient_pop in zip(source_pop_files, recipient_pop_files):
    logging.info("simulation repetition: {}".format(sim_count))
    sim_count += 1

    simulation_outputs = []
    for i in range(analysis_params["analysis repetitions"]):
      logging.info("\tanalysis repetition: {}".format(i + 1))
      analysis_params["source population file"] = source_pop
      analysis_params["recipient population file"] = recipient_pop
      analysis = Analysis.from_params(analysis_params)
      analysis.perform_analysis()
      simulation_outputs.append(analysis.get_output())

    average_analysis_output = average_analysis_outputs(simulation_outputs)
    average_analysis_output.update(run_params)
    average_analysis_output.update(analysis_params)
    all_simulation_outputs.append(average_analysis_output)

  print(json.dumps(all_simulation_outputs))
