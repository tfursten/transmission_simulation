import random
from statistics import mean

from Tree import Tree
from Population import Population


class Analysis:
  def __init__(self):
    self.source_pop = None
    self.recipient_pop = None
    self.sample_size = None
    self.num_clumpiness_bins = None
    self.results = {}

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
    obj.num_clumpiness_bins = analysis_params["number clumpiness bins"]
    obj.count_populations = bool(int(analysis_params["count populations"]))
    return obj

  def perform_analysis(self):
    for source_genome in self.source_pop.sample:
      for recipient_genome in self.recipient_pop.sample:
        tree = Tree.initialized(source_genome, recipient_genome, 
                                self.source_pop, self.recipient_pop)
        self.collect_tree_results(tree)

  def collect_tree_results(self, tree):
    self.collect_tree_result(tree, "tier 1", tree.check_tier_1)
    self.collect_tree_result(tree, "tier 2", tree.check_tier_2)
    self.collect_tree_result(tree, 
                            "clumpiness ancestral", 
                            tree.check_clumpiness_ancestral)
    self.collect_tree_result(tree, 
                            "clumpiness composite", 
                            tree.check_clumpiness_composite)
    self.collect_tree_result(tree, "combined", self.get_combined_values)

  def collect_tree_result(self, tree, statistic, check_function):
    if statistic not in self.results:
      self.results[statistic] = {
        "correct detection": [],
        "reverse detection": []
      }

    if statistic in ["clumpiness ancestral", "clumpiness composite"]:
      result = check_function(self.num_clumpiness_bins)
    else:
      result = check_function()

    self.results[statistic]["correct detection"].append(
      result["correct detection"] 
    )
    self.results[statistic]["reverse detection"].append(
      result["reverse detection"] 
    )

  def get_combined_values(self):
    statistics = [key for key in self.results if key != "combined"]
    correct_values = [
      self.results[statistic]["correct detection"][-1] 
      for statistic in statistics
    ] 
    reverse_values = [
      self.results[statistic]["reverse detection"][-1] 
      for statistic in statistics
    ] 

    return {
      "correct detection": any(correct_values),
      "reverse detection": any(reverse_values)
    }
  
  def count_ambiguous_detection(self):
    """
    Tallies the situations in which neither a 'correct' nor a 'reverse'
    transmission direction is called (i.e. ambiguous transmission), for each
    statistic.
    """
    num_analyses = len(self.results["tier 1"]["correct detection"])
    for statistic in self.results:
      self.results[statistic]["ambiguous detection"] = []
      for i in range(num_analyses):
        if (self.results[statistic]["correct detection"][i] == 0 
            and self.results[statistic]["reverse detection"][i] == 0):
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
          self.results.unique_source_pop_genomes,
        "unique genomes in source sample": 
          self.results.unique_source_sample_genomes,
        "unique genomes in recipient population": 
          self.results.unique_recipient_pop_genomes,
        "unique genmoes in recipient sample":
          self.results.unique_recipient_sample_genomes,
      }
      output.update(population_counts)

    return output

