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
    self.results = {
      "tier 1": {
        "values": {
          "correct detection": [],
          "reverse detection": []
        },
        "proportion": {
          "correct detection": None,
          "reverse detection": None
        }
      },
      "tier 2": {
        "values": {
          "correct detection": [],
          "reverse detection": []
        },
        "proportion": {
          "correct detection": None,
          "reverse detection": None
        }
      },
      "clumpiness": {
        "values": {
          "correct detection": [],
          "reverse detection": []
        },
        "proportion": {
          "correct detection": None,
          "reverse detection": None
        }
      },
      "combined": {
        "values": {
          "correct detection": [],
          "reverse detection": []
        },
        "proportion": {
          "correct detection": None,
          "reverse detection": None
        }
      },
      "population counts": {
        "source population": 0,
        "source sample": 0,
        "recipient population": 0,
        "recipient sample": 0
      }
    }

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
    self.results["combined"]["values"]["correct detection"].append(0)
    self.results["combined"]["values"]["reverse detection"].append(0)
    for statistic, function in [
        ("tier 1", tree.check_tier_1),
        ("tier 2", tree.check_tier_2), 
        ("clumpiness", tree.compare_clumpiness) 
    ]:
      if statistic == "clumpiness":
          output = function(tree.shared_branch, self.num_clumpiness_bins)
      else:
        output = function()
        
      for type in ("correct detection", "reverse detection"):
        self.results[statistic]["values"][type].append(output[type]) 
        if output[type] == 1:
          self.results["combined"]["values"][type][-1] = 1

  def count_populations(self):
    population_names = ("source population", "source sample", 
                       "recipient population", "recipient sample")
    populations = (self.source_pop.population, self.source_pop.sample, 
                   self.recipient_pop.population, self.recipient_pop.sample)

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
    for statistic in ("tier 1", "tier 2", "clumpiness", "combined"):
      self.results[statistic]["proportion"] = {
        "correct detection": 
          mean(self.results[statistic]["values"]["correct detection"]),
        "reverse detection": 
          mean(self.results[statistic]["values"]["reverse detection"])
      }

  def get_output(self):
    self.get_proportions()
    output = {
      "tier 1 proportion": self.results["tier 1"]["proportion"],
      "tier 2 proportion": self.results["tier 2"]["proportion"],
      "clumpiness proportion": self.results["clumpiness"]["proportion"],
      "combined proportion": self.results["combined"]["proportion"],
    }
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

