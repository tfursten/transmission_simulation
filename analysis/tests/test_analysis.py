import pytest

from ..Analysis import Analysis
from ..Genome import Genome
from ..Population import Population
from ..analyze import calc_proportions


class TestAnalysis:
    @pytest.fixture
    def analysis(self):
        source_genomes = [
            Genome([1, 2, 3, 4]),
            Genome([1, 2, 5, 6]),
        ]
        source_pop = Population()
        source_pop.sample = source_genomes
        source_pop.get_sample_snps()
        recipient_genomes = [
            Genome([1, 2, 3, 4, 5]),
            Genome([1, 3, 5]),
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

        assert len(analysis.results) == 4
        assert list(analysis.results["tier 1"]) == [0, 1, 0, 1]
        assert list(analysis.results["tier 2"]) == [1, -1, 1, 0]
        assert list(analysis.results["clumpiness"]) == [0, 1, -1, 0]

        proportions = calc_proportions(analysis.results)
        assert len(proportions) == 1
