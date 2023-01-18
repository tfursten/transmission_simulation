import pytest
import os

from Population import Population
from Genome import Genome
from Tree import Tree


class TestPopulation:
  def test_parse_csv(self):
    with open("test_file.csv", 'w') as file:
      file.write("200,12345,2700000,3,0\n")
      file.write("4600,300500,13,\n")
      file.write("\n")
      file.write("7,\n")

    pop = Population()
    pop.population = pop.parse_csv("test_file.csv")

    assert len(pop.population) == 3
    assert len(pop.population[0].mutations) == 5
    assert pop.population[1].mutations == [4600, 300500, 13]
  
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

    pop = Population()
    snps = pop.get_sample_snps(sample)
    
    assert len(snps) == 7
    assert 7 not in snps
    assert snps[1]["count"] == 4
    assert snps[1]["proportion"] == 1
    assert snps[3]["proportion"] == 0.75 
    assert snps[8]["proportion"] == 0.25
    
    print(snps)

  def teardown_class(cls):
    os.remove("test_file.csv")


class TestGenome:
  def test_is_unique_in_population(self):
    pop = [
      g1 := Genome([1,2,3,4]),
      g2 := Genome([1,2,3,4,5]),
      Genome([1,2,3,4]),
    ]

    assert not g1.is_unique_in_population(pop)
    assert g2.is_unique_in_population(pop)


class TestTree:
  @pytest.fixture
  def source_pop(self):
    genomes = [
      Genome([1,2,3,4,8]),
      Genome([1,2,3,4,5]),
      Genome([1,3]),
    ]
    return Population.from_genomes(genomes, 10)

  @pytest.fixture
  def recipient_pop(self):
    genomes = [
      Genome([1,2,3,7]),
      Genome([1,2,3,4,5]),
      Genome([1,2,4]),
    ]
    return Population.from_genomes(genomes, 10)
  
  @pytest.fixture
  def branches(self, source_pop, recipient_pop):
    tree = Tree()
    src_genome = source_pop.population[0]
    rec_genome = recipient_pop.population[0]
    branches = tree.categorize_mutations(src_genome, rec_genome)
    return branches

  def test_categorize_mutations(self, branches):
    shared_branch, source_branch, recipient_branch = branches.values()
    assert list(shared_branch.keys()) == [1,2,3]
    assert list(source_branch.keys()) == [4,8]
    assert list(recipient_branch.keys()) == [7]

  def test_assign_proportions(self, branches, source_pop, recipient_pop):
    tree = Tree()
    branches_proportions = tree.assign_proportions(branches, source_pop, 
                                                   recipient_pop) 

    shared_proportions, source_proportions, recipient_proportions = \
      branches_proportions.values()
    
    assert list(shared_proportions.keys()) == [1,2,3]
    assert list(source_proportions.keys()) == [4,8]
    assert list(recipient_proportions.keys()) == [7]
    

