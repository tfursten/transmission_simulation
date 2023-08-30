import glob
import gzip
import json
import logging
import os
import shutil
import sys

from .Analysis import Analysis

logging.getLogger().setLevel(logging.INFO)


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

  keys_of_interest = (
    "tier 1", "tier 2", "clumpiness tally", "clumpiness magnitude", "combined"
  )
  accumulator = {k: outputs[0][k] for k in keys_of_interest}

  for sim in outputs[1:]:
    for key in keys_of_interest:
      for detection in detections:
        accumulator[key][detection] += sim[key][detection]

  for key in accumulator:
    for detection in detections:
      accumulator[key][detection] /= len(outputs)

  return accumulator

# python -m analysis.analyze analysis_params.json
if __name__ == "__main__":
  analysis_params_file = sys.argv[1]

  with open(analysis_params_file, 'r') as file:
    analysis_params = json.load(file)

  sim_params_file = analysis_params["path to simulation parameters"]
  with open(sim_params_file, "r") as file:
    sim_params = json.load(file)

  # find all population files belonging to simulation
  pop_files_dir = analysis_params["path to simulation files"]
  sim_id = sim_params["run_id"]
  pop_files_pattern = \
    os.path.join(pop_files_dir, "run_" + str(sim_id) + "*pop*csv.gz")
  pop_files = glob.glob(pop_files_pattern)
  source_pop_files = [file for file in pop_files if "source" in file]
  recipient_pop_files = [file for file in pop_files if "recipient" in file]

  # decompress .gz files
  for file in source_pop_files + recipient_pop_files:
    if '.gz' in file:
      with gzip.open(file, 'rb') as fh_in:
        with open(file.replace('.gz', ''), 'wb') as fh_out:
          shutil.copyfileobj(fh_in, fh_out)
  source_pop_files = [f.replace('.gz', '') for f in source_pop_files]
  recipient_pop_files = [f.replace('.gz', '') for f in recipient_pop_files]

  # ensure files from matching simulation runs are analyzed together
  source_pop_files.sort()
  recipient_pop_files.sort()

  # perform analyses
  all_sim_outputs = []
  sim_count = 1
  for source_pop, recipient_pop in zip(source_pop_files, recipient_pop_files):
    logging.info("simulation repetition: {}".format(sim_count))
    sim_count += 1

    sim_outputs = []
    for i in range(analysis_params["analysis repetitions"]):
      logging.info("\tanalysis repetition: {}".format(i + 1))
      analysis_params["source population file"] = source_pop
      analysis_params["recipient population file"] = recipient_pop
      analysis = Analysis.from_params(analysis_params)
      analysis.perform_analysis()
      sim_outputs.append(analysis.get_output())

    average_analysis_output = average_analysis_outputs(sim_outputs)
    average_analysis_output.update(sim_params)
    average_analysis_output.update(analysis_params)
    average_analysis_output.update(analysis.raw)
    all_sim_outputs.append(average_analysis_output)

  filename = (
    f"src{sim_params['source generations']}-"
    f"rec{sim_params['recipient generations']}-"
    f"bot{sim_params['bottleneck']}-"
    f"cmb{analysis_params['combination number']}"
    ".json"
  )
  with open(filename, 'w') as fh:
    json.dump(all_sim_outputs, fh)

  # remove uncompressed output files
  for file in source_pop_files + recipient_pop_files:
    assert os.path.exists(file + '.gz')
    os.remove(file)
