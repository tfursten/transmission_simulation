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
    analysis.num_clumpiness_bins = 0

    return analysis

  def test_perform_analysis(self, analysis):
    analysis.combination_size = 1
    analysis.perform_analysis()
    assert analysis.results.analyses == 4
    assert analysis.results.trees == 4
    assert len(analysis.results.tier1_values) == 4
    assert analysis.results.tier1_values == [0, 1, 0, 1]
    assert analysis.results.tier2_values == [1, 0, 1, 0]
    assert analysis.results.combined_values == [1, 1, 1, 1]

    analysis.combination_size = 2
    analysis.results.analyses = 0
    analysis.results.trees = 0
    analysis.results.tier1_values = []
    analysis.sample_size = 3 # not actually
    analysis.perform_analysis()
    assert analysis.results.analyses == analysis.analyses == 50_000
    assert analysis.results.trees == 200_000 # combosize^2 * analyses 
    assert len(analysis.results.tier1_values) == analysis.analyses

  def test_calculate_output(self, analysis):
    analysis.combination_size = 1
    analysis.perform_analysis()
    analysis.calculate_output()
    assert analysis.output.analyses == 4
    assert analysis.output.trees == 4
    assert analysis.output.tier1_proportion == 0.5
    assert analysis.output.tier2_proportion == 0.5
    assert analysis.output.combined_proportion == 1
