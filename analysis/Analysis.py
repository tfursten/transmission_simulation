import random
from dataclasses import dataclass
from statistics import mean

from Tree import Tree
from Population import Population

class Analysis:
  def __init__(self):
    self.source_pop = None
    self.recipient_pop = None
    self.sample_size = None
    self.combination_size = None
    self.num_clumpiness_bins = None
    self.analyses = 50_000
    
    @dataclass
    class Results:
      analyses = 0
      trees = 0
      tier1_values = []
      tier2_values = []
      clumpiness_values = []
      combined_values = []
    self.results = Results()

    @dataclass
    class Output:
      analyses = 0
      trees = 0
      source_pop_unique_genomes = None 
      source_sample_unique_genomes = None 
      recipient_pop_unique_genomes = None
      recipient_sample_unique_genomes = None 
      tier1_proportion = 0
      tier2_proportion = 0
      clumpiness_proportion = 0
      combined_proportion = 0
    self.output = Output()

  @classmethod
  def from_params(cls, analysis_params):
    obj = cls()
    obj.sample_size = analysis_params.sample_size
    obj.source_pop = \
      Population.from_csv_file(analysis_params.source_population_file,
                               obj.sample_size)
    obj.recipient_pop = \
      Population.from_csv_file(analysis_params.recipient_population_file,
                               obj.sample_size)
    obj.combination_size  = analysis_params.combination_size
    obj.num_clumpiness_bins = analysis_params.num_clumpiness_bins

    return obj

  def perform_analysis(self):
    assert self.combination_size > 0
    assert self.combination_size < self.sample_size

    if self.combination_size > 1:
      # exploring all combinations not feasible
      # even at combination_size = 2 there are 100M (100^4) possible samplings 
      for _ in range(self.analyses):
        self.results.analyses += 1

        source_genomes = [random.choice(self.source_pop.sample) 
                          for _ in range(self.combination_size)]
        recipient_genomes = [random.choice(self.recipient_pop.sample) 
                            for _ in range(self.combination_size)]

        for source_genome in source_genomes:
          for recipient_genome in recipient_genomes:
            tree = Tree.initialized(source_genome, recipient_genome, 
                                    self.source_pop, self.recipient_pop)
            self.collect_tree_results(tree)
        
        self.detect_with_combination()

    else:
      for source_genome in self.source_pop.sample:
        for recipient_genome in self.recipient_pop.sample:
          self.results.analyses += 1
          tree = Tree.initialized(source_genome, recipient_genome, 
                                  self.source_pop, self.recipient_pop)
          self.collect_tree_results(tree)

  def detect_with_combination(self):
    trees_per_detection = self.combination_size ** 2
    for all_values in (self.results.tier1_values, 
                   self.results.tier2_values,
                   self.results.clumpiness_values, 
                   self.results.combined_values):
      tree_values = all_values[-trees_per_detection:]
      del all_values[-trees_per_detection:]
      all_values.append(1 if any(tree_values) else 0)

  def collect_tree_results(self, tree):
    self.results.trees += 1
    tier1_value = tree.check_tier_1()
    self.results.tier1_values.append(tier1_value) 
    tier2_value = tree.check_tier_2()
    self.results.tier2_values.append(tier2_value)
    clumpiness_value = \
      tree.compare_clumpiness(tree.shared_branch, self.num_clumpiness_bins)
    self.results.clumpiness_values.append(clumpiness_value)

    combined_value = int(any([tier1_value, tier2_value, clumpiness_value]))
    self.results.combined_values.append(combined_value)

  def calculate_output(self, count_populations=False):
    self.output.analyses = self.results.analyses
    self.output.trees = self.results.trees
    if count_populations:
      self.output.source_pop_unique_genomes = \
        self.source_pop.count_unique_genomes(self.source_pop.population)
      self.output.source_sample_unique_genomes = \
        self.source_pop.count_unique_genomes(self.source_pop.sample)
      self.output.recipient_pop_unique_genomes = \
        self.recipient_pop.count_unique_genomes(self.recipient_pop.population)
      self.output.recipient_sample_unique_genomes = \
        self.recipient_pop.count_unique_genomes(self.recipient_pop.sample)
    
    self.output.tier1_proportion = mean(self.results.tier1_values) 
    self.output.tier2_proportion = mean(self.results.tier2_values)
    self.output.clumpiness_proportion = mean(self.results.clumpiness_values)
    self.output.combined_proportion = mean(self.results.combined_values)
    
  def get_output(self):
    output = {
      "analyses": self.output.analyses,
      "trees": self.output.trees,
      "tier 1 proportion": self.output.tier1_proportion,
      "tier 2 proportion": self.output.tier2_proportion,
      "clumpiness proportion": self.output.clumpiness_proportion,
      "combined proportion": self.output.combined_proportion,
    }
    if self.output.source_pop_unique_genomes is not None:
      population_counts = {
        "unique genomes in source population": 
          self.output.source_pop_unique_genomes,
        "unique genomes in source sample": 
          self.output.source_sample_unique_genomes,
        "unique genomes in recipient population": 
          self.output.recipient_pop_unique_genomes,
        "unique genmoes in recipient sample":
          self.output.recipient_sample_unique_genomes,
      }
      output.update(population_counts)

    return output

