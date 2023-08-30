import random
from statistics import mean

from .Tree import Tree
from .Population import Population


class Analysis:
  def __init__(self):
    self.source_pop = None
    self.recipient_pop = None
    self.sample_size = None
    self.num_bins = None
    self.combination_number = None
    self.results = {}
    self.raw = {}

  @classmethod
  def from_params(cls, analysis_params):
    obj = cls()
    obj.sample_size = analysis_params["sample size"]
    obj.source_pop = \
      Population.from_csv_file(analysis_params["source population file"],
                               obj.sample_size)
    obj.recipient_pop = \
      Population.from_csv_file(analysis_params["recipient population file"],
                               obj.sample_size)
    obj.num_bins = analysis_params["number bins"]
    obj.count_populations = bool(int(analysis_params["count populations"]))
    obj.combination_number = analysis_params["combination number"]
    return obj

  def perform_analysis(self):
    if self.combination_number == 1:
      for source_genome in self.source_pop.sample:
        for recipient_genome in self.recipient_pop.sample:
          tree = Tree.initialized(source_genome, recipient_genome, 
                                  self.source_pop, self.recipient_pop)
          self.collect_tree_results([tree])
    else:
      for _ in range(10_000):
        trees = []
        for c in range(self.combination_number): 
          source_genome = random.choice(self.source_pop.sample)
          recipient_genome = random.choice(self.recipient_pop.sample)
          tree = Tree.initialized(source_genome, recipient_genome, 
                                  self.source_pop, self.recipient_pop)
          trees.append(tree)

        if len(trees) != self.combination_number:
          raise ValueError("Number of trees not equal to combination number")
        self.collect_tree_results(trees)


  def collect_tree_results(self, trees):
    self.collect_tier_1(trees)
    self.collect_tier_2(trees)
    self.collect_clumpiness_composite(trees)
    self.get_combined_values()

  def collect_tier_1(self, trees):
    tier_1_results = [tree.check_tier_1() for tree in trees]
    max_src_seg = max(
      map(lambda r: r["source segregating"], tier_1_results))
    max_rec_seg = max(
      map(lambda r: r["recipient segregating"], tier_1_results))

    correct = int(max_src_seg > max_rec_seg)
    reverse = int(max_src_seg < max_rec_seg)
    self.add_result(correct, reverse, "tier 1")

    self.add_raw(max_src_seg, max_rec_seg, "tier 1")
  
  def collect_tier_2(self, trees):
    tier_2_results = [tree.check_tier_2() for tree in trees]
    max_src_on_rec = max(
      map(lambda r: r["source segregating on recipient"], tier_2_results))
    max_rec_on_src = max(
      map(lambda r: r["recipient segregating on source"], tier_2_results))
    
    # note: tier 2 definition is changed here, otherwise maximizing works
    # strongly against us, pushing rec_on_src above zero 
    # old definition:
    # correct = src_on_rec > 0 and rec_on_src == 0 
    # reverse = rec_on_src > 0 and src_on_rec == 0
    correct = int(max_src_on_rec > max_rec_on_src)
    reverse = int(max_src_on_rec < max_rec_on_src)
    self.add_result(correct, reverse, "tier 2")

    self.add_raw(max_src_on_rec, max_rec_on_src, "tier 2")

  def collect_clumpiness_composite(self, trees):
    clumpiness_results = \
      [tree.check_clumpiness_composite(self.num_bins) for tree in trees]
    
    tally = {'correct': 0, 'reverse': 0}
    diff = {'source diff': [], 'recipient diff': []}
    for result in clumpiness_results:
      src_on_src = result["ancestral to source lineage"]["source"]
      rec_on_src = result["ancestral to source lineage"]["recipient"]
      rec_on_rec = result["ancestral to recipient lineage"]["recipient"]
      src_on_rec = result["ancestral to recipient lineage"]["source"]

      # tally
      if src_on_src >= rec_on_src:
        if src_on_rec >= rec_on_rec:
          correct = 1
          reverse = 0
        elif src_on_rec < rec_on_rec:
          correct = 0
          reverse = 0
      elif src_on_src < rec_on_src:
        if rec_on_rec >= src_on_rec:
          correct = 0
          reverse = 1
        elif rec_on_rec < src_on_rec:
          correct = 0
          reverse = 0

      tally['correct'] += correct
      tally['reverse'] += reverse
      
      # magnitude
      if rec_on_src == 0:
        rec_on_src = 1
        src_on_src += 1
      if rec_on_rec == 0:
        rec_on_rec = 1
        src_on_rec += 1
      diff['source diff'].append(src_on_src / rec_on_src)
      diff['recipient diff'].append(src_on_rec / rec_on_rec)

    # tally
    if tally['correct'] > tally['reverse']:
      correct, reverse = 1, 0
    elif tally['correct'] == tally['reverse']:
      correct, reverse = 0, 0
    else:
      correct, reverse = 0, 1

    self.add_result(correct, reverse, "clumpiness tally")
    self.add_raw(correct, reverse, "clumpiness tally")

    # magnitude
    source_diff = sum(diff['source diff']) / len(diff['source diff'])
    recipient_diff = sum(diff['recipient diff']) / len(diff['recipient diff'])
    if source_diff > 1:
      if recipient_diff > 1:
        correct, reverse = 1, 0
      elif recipient_diff <= 1:
        correct, reverse = 0, 0
    elif source_diff <= 1:
      if recipient_diff <= 1:
        correct, reverse = 0, 1
      elif recipient_diff > 1:
        correct, reverse = 0, 0

    self.add_result(correct, reverse, "clumpiness magnitude")
    self.add_raw(correct, reverse, "clumpiness magnitude")

  def get_combined_values(self):
    statistics = "tier 1", "tier 2"
    correct_values = [
      self.results[statistic]["correct detection"][-1] 
      for statistic in statistics
    ] 
    reverse_values = [
      self.results[statistic]["reverse detection"][-1] 
      for statistic in statistics
    ] 

    correct = int(any(correct_values))
    reverse = int(any(reverse_values))
    self.add_result(correct, reverse, "combined")
  
  def add_raw(self, correct, reverse, statistic):
    if f"raw {statistic}" not in self.raw:
      self.raw[f"raw {statistic}"] = {
        "correct detection": [],
        "reverse detection": []
      }
    self.raw[f"raw {statistic}"]["correct detection"].append(correct)
    self.raw[f"raw {statistic}"]["reverse detection"].append(reverse)

  def add_result(self, correct, reverse, statistic):
    if statistic not in self.results:
      self.results[statistic] = {
        "correct detection": [],
        "reverse detection": []
      }
    self.results[statistic]["correct detection"].append(correct)
    self.results[statistic]["reverse detection"].append(reverse)

  def count_ambiguous_detection(self):
    """
    Tallies the situations in which neither a 'correct' nor a 'reverse'
    transmission direction is called, or both are called 
    (i.e. ambiguous transmission), for each statistic.
    """
    num_analyses = len(self.results["tier 1"]["correct detection"])
    for statistic in self.results:
      self.results[statistic]["ambiguous detection"] = []
      for i in range(num_analyses):
        if (self.results[statistic]["correct detection"][i] == 0 
            and self.results[statistic]["reverse detection"][i] == 0):
          self.results[statistic]["ambiguous detection"].append(1)
        elif (self.results[statistic]["correct detection"][i] == 1 
            and self.results[statistic]["reverse detection"][i] == 1):
          self.results[statistic]["ambiguous detection"].append(1)
        else:
          self.results[statistic]["ambiguous detection"].append(0) 

  def count_populations(self):
    population_names = ("source population", "source sample", 
                       "recipient population", "recipient sample")
    populations = (self.source_pop.population, self.source_pop.sample, 
                   self.recipient_pop.population, self.recipient_pop.sample)

    self.results["population counts"] = {}
    for pop_name, pop in zip(population_names, populations):
      self.results["population counts"][pop_name] = \
        self.count_unique_genomes(pop)
  
  def count_unique_genomes(self, population):
    unique_counter = 0
    visited_genomes = []
    for genome in population:
      if genome not in visited_genomes:
        visited_genomes.append(genome)
        unique_counter += 1

    return unique_counter

  def get_proportions(self):
    proportions = {}
    for statistic in self.results:
      proportions[statistic] = {}
      for direction in ("correct", "reverse", "ambiguous"):
        proportions[statistic][f"{direction} detection proportion"] = \
          mean(self.results[statistic][f"{direction} detection"])
    
    return proportions

  def get_output(self):
    self.count_ambiguous_detection()
    output = self.get_proportions()

    if self.count_populations:
      self.count_populations()
      population_counts = {
        "unique genomes in source population": 
          self.results["population counts"]["source population"],
        "unique genomes in source sample": 
          self.results["population counts"]["source sample"],
        "unique genomes in recipient population": 
          self.results["population counts"]["recipient population"],
        "unique genmoes in recipient sample":
          self.results["population counts"]["recipient sample"],
      }
      output.update(population_counts)

    return output
