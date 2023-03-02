import pytest

import sys
sys.path.append("../")
from Tree import Tree
from Population import Population
from Genome import Genome

class TestTree:
  @pytest.fixture
  def source_pop(self):
    genomes = [
      Genome([1,2,3,4,8]), # clone
      Genome([1,2,3,4,5]),
      Genome([1,3]),
    ]
    pop = Population()
    pop.sample = genomes
    pop.get_sample_snps()
    return pop

  @pytest.fixture
  def recipient_pop(self):
    genomes = [
      Genome([1,2,3,7]), # clone
      Genome([1,2,3,4,5]),
      Genome([1,2,4]),
    ]
    pop = Population()
    pop.sample = genomes
    pop.get_sample_snps()
    return pop

  @pytest.fixture
  def tree(self, source_pop, recipient_pop):
    return Tree.initialized(source_pop.sample[0],
                            recipient_pop.sample[0],
                            source_pop,
                            recipient_pop)

  def test_categorize_mutations(self, tree):
    assert list(tree.shared_branch.keys()) == [1,2,3]
    assert list(tree.source_branch.keys()) == [4,8]
    assert list(tree.recipient_branch.keys()) == [7]

  def test_assign_proportions(self, tree):
    assert tree.shared_branch[1]["source_proportion"] == 1
    assert tree.shared_branch[1]["recipient_proportion"] == 1
    assert tree.shared_branch[2]["source_proportion"] == 2/3
    assert tree.shared_branch[3]["recipient_proportion"] == 2/3
    assert 5 not in tree.shared_branch
    assert tree.source_branch[8]["source_proportion"] == 1/3
    assert tree.source_branch[8]["recipient_proportion"] == 0
    assert tree.recipient_branch[7]["recipient_proportion"] == 1/3
    assert tree.recipient_branch[7]["source_proportion"] == 0
    
  def test_count_segregating_snps(self):
    branch = {
      1: {
        "source_proportion": 0.6,
        "recipient_proportion": 1,
      },
      2: {
        "source_proportion": 0.9,
        "recipient_proportion": 1,
      },
      3: {
        "source_proportion": 0,
        "recipient_proportion": 0,
      },
      4: {
        "source_proportion": 1,
        "recipient_proportion": 0,
      },
    }
    tree = Tree()
    src_segs = tree.count_segregating_snps("source", branch)
    rec_segs = tree.count_segregating_snps("recipient", branch)
    assert src_segs == 2
    assert rec_segs == 0

    src_genomes = [
      Genome([1,2,3,4,5,7]), # clone
      Genome([1,2,4,5]),
      Genome([1,2,3,8]),
    ]
    source_pop = Population.from_genomes(src_genomes, 20)
    rec_genomes = [
      Genome([1,2,3,4,6,9]), # clone
      Genome([1,2,3,4,5]),
      Genome([1,2,4]),
    ]
    recipient_pop = Population.from_genomes(rec_genomes, 20)
    tree = Tree.initialized(src_genomes[0], rec_genomes[0], source_pop, 
                            recipient_pop)
    shared_src_segs = tree.count_segregating_snps("source", tree.shared_branch)
    assert shared_src_segs == 2, "may fail due to random sampling" # [3,4]
    shared_rec_segs = tree.count_segregating_snps("recipient", 
                                                  tree.shared_branch)
    assert shared_rec_segs == 1, "may fail due to random sampling" # [3]

  def test_check_tier_1(self):
    tree = Tree()
    tree.shared_branch = {}
    assert tree.check_tier_1() == \
      {
        "correct detection": 0,
        "reverse detection": 0
      }

    tree.shared_branch = {
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
    assert tree.check_tier_1() == \
      {
        "correct detection": 1,
        "reverse detection": 0
      }

    tree.shared_branch[1]["source_proportion"] = 1
    assert tree.check_tier_1() == \
      {
        "correct detection": 0,
        "reverse detection": 0
      }

    tree.shared_branch[2]["recipient_proportion"] = 0.4
    assert tree.check_tier_1() == \
      {
        "correct detection": 0,
        "reverse detection": 1
      }
  

  def test_check_tier_2(self):
    tree = Tree()
    tree.source_branch = {}
    tree.recipient_branch = {}
    assert tree.check_tier_2() == \
      {
        "correct detection": 0,
        "reverse detection": 0
      }

    tree.source_branch = {
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
    tree.recipient_branch = {
      4: {
        "source_proportion": 0.5,
        "recipient_proportion": 1, 
      },
      5: {
        "source_proportion": 1,
        "recipient_proportion": 1, 
      },
      6: {
        "source_proportion": 1,
        "recipient_proportion": 0.9, 
      },
    }
    assert tree.check_tier_2() == \
      {
        "correct detection": 1,
        "reverse detection": 0
      }

    tree.recipient_branch[4]["source_proportion"] = 1
    assert tree.check_tier_2() == \
      {
        "correct detection": 0,
        "reverse detection": 0
      }

    tree.source_branch[1]["recipient_proportion"] = 0.9
    tree.recipient_branch[4]["source_proportion"] = 0.5
    assert tree.check_tier_2() == \
      {
        "correct detection": 0,
        "reverse detection": 0
      }
    
    tree.source_branch[1]["recipient_proportion"] == 0.5
    tree.recipient_branch[4]["source_proportion"] = 1
    assert tree.check_tier_2() == \
      {
        "correct detection": 0,
        "reverse detection": 1
      }


  def test_bin_proportions(self):
    tree = Tree()
    assert tree.bin_proportions([], num_bins=1) == []
    assert tree.bin_proportions([1], num_bins=1) == [1]
    assert tree.bin_proportions([1,1], num_bins=2) == [0,2]
    assert tree.bin_proportions([1,1], num_bins=1) == [2]
    assert tree.bin_proportions([1, 0.1, 1], num_bins=2) == [1, 2]
    assert tree.bin_proportions([1, 0, 0], num_bins=2) == [2, 1] 

    proportions = [1, 0.4, 0.8, 1]
    binned_proportions = tree.bin_proportions(proportions, num_bins=10)
    assert binned_proportions == [0, 0, 0, 1, 0, 0, 0, 1, 0, 2]


  def test_psuedo_entropy(self):
    tree = Tree()
    assert tree.psuedo_entropy([]) == 0
    assert tree.psuedo_entropy([1]) == 0
    assert tree.psuedo_entropy([30]) == 0
    assert tree.psuedo_entropy([0, 1]) == 0
    assert tree.psuedo_entropy([0, 99]) == 0
    assert tree.psuedo_entropy([1, 1]) == 1

    source_proportions_binned = [0, 0, 1, 3, 3]
    recipient_proportions_binned = [0, 0, 0, 0, 7]
    source_entropy = tree.psuedo_entropy(source_proportions_binned)
    recipient_entropy = tree.psuedo_entropy(recipient_proportions_binned)
    assert source_entropy > recipient_entropy

    source_entropy = tree.psuedo_entropy([1, 1, 0, 0, 0])
    recipient_entropy = tree.psuedo_entropy([1, 0, 0, 0, 1])
    assert source_entropy == recipient_entropy

    # important to understand the phylogenetic implications of this one 
    source_entropy = tree.psuedo_entropy([3, 1, 0, 0])
    recipient_entropy = tree.psuedo_entropy([2, 2, 0, 0])
    assert source_entropy < recipient_entropy

    # problem with entropy as proxy for diversity:
    print("source:", tree.psuedo_entropy([5,1,1,1,1,1]))
    print("recipient:", tree.psuedo_entropy([0,3,0,2,3,2]))


  def test_check_clumpiness(self):
    tree = Tree()
    assert tree.check_clumpiness({}, num_bins=10) == \
      {
        "source entropy": 0,
        "recipient entropy": 0
      }

    branch = {
      1: {
        "source_proportion": 1,
        "recipient_proportion": 1
      }
    }
    assert tree.check_clumpiness(branch, num_bins=10) == \
      {
        "source entropy": 0,
        "recipient entropy": 0
      }

    branch = {
      1: {
        "source_proportion": 1,
        "recipient_proportion": 1
      },
      2: {
        "source_proportion": 0.5,
        "recipient_proportion": 1
      }
    }
    entropys = tree.check_clumpiness(branch, num_bins=10)
    assert entropys["source entropy"] > entropys["recipient entropy"]

  
  def test_check_clumpiness_ancestral(self):
    tree = Tree()
    assert tree.check_clumpiness_ancestral(num_bins=10) == \
      {
        "correct detection": 0,
        "reverse detection": 0
      }

    tree.shared_branch = {
      1: {
        "source_proportion": 1,
        "recipient_proportion": 1
      },
      2: {
        "source_proportion": 0.8,
        "recipient_proportion": 1
      },
      3: {
        "source_proportion": 0.5,
        "recipient_proportion": 0.8
      }
    }
    assert tree.check_clumpiness_ancestral(num_bins=10) == \
      {
        "correct detection": 1,
        "reverse detection": 0
      }

    tree.shared_branch = {
      1: {
        "source_proportion": 1,
        "recipient_proportion": 1
      },
      2: {
        "source_proportion": 1,
        "recipient_proportion": 0.9
      },
      3: {
        "source_proportion": 0.5,
        "recipient_proportion": 0.8
      }
    }
    assert tree.check_clumpiness_ancestral(num_bins=10) == \
      {
        "correct detection": 0,
        "reverse detection": 1
      }

    tree.shared_branch = {
      1: {
        "source_proportion": 1,
        "recipient_proportion": 1
      },
      2: {
        "source_proportion": 0.5,
        "recipient_proportion": 0.8
      }
    }
    assert tree.check_clumpiness_ancestral(num_bins=10) == \
      {
        "correct detection": 0,
        "reverse detection": 0
      }
  

  def test_check_clumpiness_composite(self):
    tree = Tree()
    assert tree.check_clumpiness_composite(num_bins=10) == \
      {
        "correct detection": 0,
        "reverse detection": 0
      }
    
    tree.shared_branch = {
      1: {
        "source_proportion": 0.8,
        "recipient_proportion": 1
      },
      2: {
        "source_proportion": 0.5,
        "recipient_proportion": 1
      }
    }
    tree.source_branch = {
      3: {
        "source_proportion": 1,
        "recipient_proportion": 0
      },
      4: {
        "source_proportion": 0.5,
        "recipient_proportion": 0 
      }
    }
    tree.recipient_branch = {
      5: {
        "source_proportion": 0,
        "recipient_proportion": 1
      },
      6: {
        "source_proportion": 0.5,
        "recipient_proportion": 0.8
      }
    }
    assert tree.check_clumpiness_composite(num_bins=10) == \
      {
        "correct detection": 1,
        "reverse detection": 0
      }

    tree.shared_branch = {
      1: {
        "source_proportion": 1,
        "recipient_proportion": 1
      },
      2: {
        "source_proportion": 0.7,
        "recipient_proportion": 0.8
      }
    }
    tree.source_branch = {
      3: {
        "source_proportion": 1,
        "recipient_proportion": 0
      },
    }
    tree.recipient_branch = {
      5: {
        "source_proportion": 0,
        "recipient_proportion": 1
      },
    }
    assert tree.check_clumpiness_composite(num_bins=10) == \
      {
        "correct detection": 0,
        "reverse detection": 0
      }