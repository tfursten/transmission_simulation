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
  tree = Tree()

  @pytest.fixture
  def source_pop(self):
    genomes = [
      Genome([1,2,3,4,8]), # clone
      Genome([1,2,3,4,5]),
      Genome([1,3]),
    ]
    return Population.from_genomes(genomes, 10)

  @pytest.fixture
  def recipient_pop(self):
    genomes = [
      Genome([1,2,3,7]), # clone
      Genome([1,2,3,4,5]),
      Genome([1,2,4]),
    ]
    return Population.from_genomes(genomes, 10)
  
  @pytest.fixture
  def branches(self, source_pop, recipient_pop):
    src_genome = source_pop.population[0]
    rec_genome = recipient_pop.population[0]
    branches = self.tree.categorize_mutations(src_genome, rec_genome)
    return branches
  
  @pytest.fixture
  def proportion_branches(self, branches, source_pop, recipient_pop):
    return self.tree.assign_proportions(branches, source_pop, recipient_pop) 
     
  def test_categorize_mutations(self, branches):
    shared_branch, source_branch, recipient_branch = branches.values()
    assert list(shared_branch.keys()) == [1,2,3]
    assert list(source_branch.keys()) == [4,8]
    assert list(recipient_branch.keys()) == [7]

  def test_assign_proportions(self, proportion_branches):
    shared_proportions, source_proportions, recipient_proportions = \
      proportion_branches.values()
    
    assert list(shared_proportions.keys()) == [1,2,3]
    assert list(source_proportions.keys()) == [4,8]
    assert list(recipient_proportions.keys()) == [7]
    assert shared_proportions[1]["source_proportion"] == 1
    
  def test_count_segregating_snps(self):
    src_genomes = [
      Genome([1,2,3,4,5,7]), # clone
      Genome([1,2,4,5]),
      Genome([1,2,3,8]),
    ]
    source_pop = Population.from_genomes(src_genomes, 10)
  
    rec_genomes = [
      Genome([1,2,3,4,6,9]), # clone
      Genome([1,2,3,4,5]),
      Genome([1,2,4]),
    ]
    recipient_pop = Population.from_genomes(rec_genomes, 10)

    tree = Tree.initialized(src_genomes[0], rec_genomes[0], source_pop, 
                            recipient_pop)

    shared_src_segs = tree.count_segregating_snps("source", tree.shared_branch)
    assert shared_src_segs == 2 # [3,4]
    shared_rec_segs = tree.count_segregating_snps("recipient", 
                                                  tree.shared_branch)
    assert shared_rec_segs == 1 # [3]

  def test_check_tier_1(self):
    shared_branch = {
      1: {
        "source_proportion": 0.5,
        "recipient_proportion": 1, 
      },
      2: {
        "source_proportion": 1,
        "recipient_proportion": 1, 
      },
      3: {
        "source_proportion": 0.3,
        "recipient_proportion": 0.9, 
      },
    }
    assert self.tree.check_tier_1(shared_branch) == 1

    shared_branch[1]["source_proportion"] = 1
    assert self.tree.check_tier_1(shared_branch) == 0

    shared_branch = {}
    assert self.tree.check_tier_1(shared_branch) == 0
  
  def test_check_tier_2(self):
    source_branch = {
      1: {
        "source_proportion": 0.5,
        "recipient_proportion": 1, 
      },
      2: {
        "source_proportion": 1,
        "recipient_proportion": 1, 
      },
      3: {
        "source_proportion": 0.8,
        "recipient_proportion": 1, 
      },
    }
    recipient_branch = {
      1: {
        "source_proportion": 0.5,
        "recipient_proportion": 1, 
      },
      2: {
        "source_proportion": 1,
        "recipient_proportion": 1, 
      },
      3: {
        "source_proportion": 1,
        "recipient_proportion": 0.9, 
      },
    }
    assert self.tree.check_tier_2(source_branch, recipient_branch) == 1

    recipient_branch[1]["source_proportion"] = 1
    assert self.tree.check_tier_2(source_branch, recipient_branch) == 0

    recipient_branch[1]["source_proportion"] = 0.5
    source_branch[1]["recipient_proportion"] = 0.9
    assert self.tree.check_tier_2(source_branch, recipient_branch) == 0

    assert self.tree.check_tier_2({}, {}) == 0

  def test_psuedo_entropy(self):
    assert self.tree.psuedo_entropy([]) == 0
    assert self.tree.psuedo_entropy([1]) == 0
    assert self.tree.psuedo_entropy([30]) == 0
    assert self.tree.psuedo_entropy([0, 1]) == 0
    assert self.tree.psuedo_entropy([0, 99]) == 0
    assert self.tree.psuedo_entropy([1, 1]) == 1

    source_props_binned = [0, 0, 1, 3, 3]
    recipient_props_binned = [0, 0, 0, 0, 7]
    source_entropy = self.tree.psuedo_entropy(source_props_binned)
    recipient_entropy = self.tree.psuedo_entropy(recipient_props_binned)
    assert source_entropy > recipient_entropy

    source_entropy = self.tree.psuedo_entropy([1, 1, 0, 0, 0])
    recipient_entropy = self.tree.psuedo_entropy([1, 0, 0, 0, 1])
    assert source_entropy == recipient_entropy

    # important to understand the implications of this one phylogenetically 
    source_entropy = self.tree.psuedo_entropy([3, 1, 0, 0])
    recipient_entropy = self.tree.psuedo_entropy([2, 2, 0, 0])
    assert source_entropy < recipient_entropy

  def test_bin_proportions(self):
    assert self.tree.bin_proportions([], num_bins=1) == []
    assert self.tree.bin_proportions([1], num_bins=1) == [1]
    assert self.tree.bin_proportions([1,1], num_bins=2) == [0,2]
    assert self.tree.bin_proportions([1,1], num_bins=1) == [2]
    # assert self.tree.bin_proportions([1, 0, 1], num_bins=2) == [1, 2]

    proportions = [1, 0.4, 0.8, 1]
    binned_proportions = self.tree.bin_proportions(proportions, num_bins=10)
    assert binned_proportions == [0, 0, 0, 1, 0, 0, 0, 1, 0, 2]
