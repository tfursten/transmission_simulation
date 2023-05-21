import random
from .Genome import Genome


class Population:
  def __init__(self):
    self.population_file = None
    self.sample_size = None
    self.population = []
    self.sample = []
    self.sample_snps = {} # {mutation: {"count": _, "proportion": _ }}

  @classmethod
  def from_csv_file(cls, population_csv_file, sample_size):
    obj = cls()
    obj.population_file = population_csv_file
    obj.sample_size = sample_size
    obj.parse_csv()
    obj.sample_population()
    obj.get_sample_snps()
    return obj

  @classmethod
  def from_genomes(cls, genomes, sample_size):
    obj = cls()
    obj.sample_size = sample_size
    obj.population = genomes
    obj.sample_population()
    obj.get_sample_snps()
    return obj
    
  def parse_csv(self):
    with open (self.population_file, "r") as file:
      for line in file:
        line = line.strip().strip(',')
        if line == '':
          self.population.append(Genome([]))
        else:
          genome = self.parse_csv_line(line)
          self.population.append(genome)

  def parse_csv_line(self, line):
    return Genome([int(mutation) for mutation in line.split(",")])

  def sample_population(self):
    for _ in range(self.sample_size):
      self.sample.append(random.choice(self.population))

  def get_sample_snps(self):
    sample_size = len(self.sample)
    for genome in self.sample:
      for mutation in genome.mutations:
        if mutation in self.sample_snps:
          count = self.sample_snps[mutation]["count"]
          self.sample_snps[mutation] = \
            {
              "count": count + 1,
              "proportion": (count + 1) / sample_size,
            }  
        else:
          self.sample_snps[mutation] = \
            { "count": 1, "proportion": 1 / sample_size }

  


