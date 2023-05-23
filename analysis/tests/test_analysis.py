import pytest

from ..Analysis import Analysis
from ..Genome import Genome
from ..Population import Population


class TestAnalysis:
  @pytest.fixture  
  def analysis(self):
    source_genomes = [
      Genome([1,2,3,4]),
      Genome([1,2,5,6]), 
    ]
    source_pop = Population()
    source_pop.sample = source_genomes
    source_pop.get_sample_snps()
    recipient_genomes = [
      Genome([1,2,3,4,5]),
      Genome([1,3,5]), 
    ]
    recipient_pop = Population()
    recipient_pop.sample = recipient_genomes
    recipient_pop.get_sample_snps()
    
    analysis = Analysis()
    analysis.source_pop = source_pop
    analysis.recipient_pop = recipient_pop
    analysis.sample_size = 2
    analysis.num_bins = 10

    return analysis

  def test_perform_analysis(self, analysis):
    analysis.combination_number = 1
    analysis.perform_analysis()
    assert len(analysis.results["tier 1"]["correct detection"]) == 4
    assert analysis.results["tier 1"] == {
      "correct detection": [0, 1, 0, 1],
      "reverse detection": [0, 0, 0, 0],
    }
    assert analysis.results["tier 2"] == {
      "correct detection": [1, 0, 1, 0],
      "reverse detection": [0, 1, 0, 0],
    }
    assert analysis.results["clumpiness"] == {
      "correct detection": [1, 1, 1, 1],
      "reverse detection": [0, 0, 0, 0],
    }
    assert analysis.results["combined"] == {
      "correct detection": [1, 1, 1, 1],
      "reverse detection": [0, 1, 0, 0],
    }

  def test_get_output(self, analysis):
    analysis.combination_number = 1
    analysis.perform_analysis()
    output = analysis.get_output()

    assert analysis.results["tier 1"]["ambiguous detection"] == [1, 0, 1, 0] 
    assert analysis.results["tier 2"]["ambiguous detection"] == [0, 0, 0, 1] 
    assert analysis.results["clumpiness"]["ambiguous detection"] == [0, 0, 0, 0] 
    assert analysis.results["combined"]["ambiguous detection"] == [0, 1, 0, 0] 

    assert output["tier 1"]["correct detection proportion"] == 0.5
    assert output["tier 1"]["reverse detection proportion"] == 0
    assert output["tier 1"]["ambiguous detection proportion"] == 0.5

    assert output["tier 2"]["correct detection proportion"] == 0.5
    assert output["tier 2"]["reverse detection proportion"] == 0.25
    assert output["tier 2"]["ambiguous detection proportion"] == 0.25
    
    assert output["clumpiness"]["correct detection proportion"] == 1
    assert output["clumpiness"]["reverse detection proportion"] == 0
    assert output["clumpiness"]["ambiguous detection proportion"] == 0

    assert output["combined"]["correct detection proportion"] == 1
    assert output["combined"]["reverse detection proportion"] == 0.25
    assert output["combined"]["ambiguous detection proportion"] == 0.25
  
  def test_combination_number(self, analysis):
    pass