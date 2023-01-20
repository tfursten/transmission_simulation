from analysis.Population import Population
from analysis.Genome import Genome


class TestPopulation:
  pop = Population()

  def test_parse_csv(self):
    with open("test_file.csv", 'w') as file:
      file.write("200,12345,2700000,3,0\n")
      file.write("4600,300500,13,\n")
      file.write("\n")
      file.write("7,\n")

    self.pop.population = self.pop.parse_csv("test_file.csv")

    assert len(self.pop.population) == 3
    assert len(self.pop.population[0].mutations) == 5
    assert self.pop.population[1].mutations == [4600, 300500, 13]
  
  def test_population_from_genomes(self):
    genomes = [
      Genome([1,2,3,4]),
      Genome([]), 
      Genome([1,3,4,5,7]),
      Genome([10]),
    ]
    pop = Population.from_genomes(genomes, sample_size = 0)

    assert len(pop.population) == 4 
    assert pop.population[2].mutations == [1,3,4,5,7]
    assert pop.population[1].mutations == []

  def test_sample_population(self):
    pop = Population.from_csv_file("test_file.csv", sample_size = 10)
    
    assert len(pop.sample) == 10
    assert isinstance(pop.sample[0], Genome)
    assert len(pop.sample_population(pop.sample, 0)) == 0
     
  def test_get_sample_snps(self):
    sample = [
      Genome([1,2,3,4,5]),
      Genome([1,2,3,4]),
      Genome([1,3,4,6]),
      Genome([1,8]),
    ]

    snps = self.pop.get_sample_snps(sample)
    
    assert len(snps) == 7
    assert 7 not in snps
    assert snps[1]["count"] == 4
    assert snps[1]["proportion"] == 1
    assert snps[3]["proportion"] == 0.75 
    assert snps[8]["proportion"] == 0.25
    
    print(snps)

  def test_count_unique_genomes(self):
    assert self.pop.count_unique_genomes([]) == 0
    assert self.pop.count_unique_genomes([Genome([])]) == 1
    assert self.pop.count_unique_genomes([Genome([]), Genome([])]) == 1

    population = [
      Genome([1,2,3,4]),
      Genome([1,2,3,4]),
      Genome([1,3,4,6]),
      Genome([1,8]),
    ]
    assert self.pop.count_unique_genomes(population) == 3

  def teardown_class(cls):
    import os
    try:
      os.remove("test_file.csv")
    except OSError:
      pass