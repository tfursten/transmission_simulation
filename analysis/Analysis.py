import random

import pandas as pd

from .Tree import Tree
from .Population import Population


class Analysis:
    def __init__(self):
        self.source_pop = None
        self.recipient_pop = None
        self.sample_size = None
        self.num_bins = None
        self.combination_number = None
        self.results = pd.DataFrame({
            'tier 1': [],
            'tier 2': [],
            'clumpiness tally': [],
            'clumpiness magnitude': [],
        })

    @classmethod
    def from_params(cls, analysis_params):
        obj = cls()
        obj.sample_size = analysis_params["sample size"]
        obj.source_pop = Population.from_csv_file(
            analysis_params["source population file"], obj.sample_size
        )
        obj.recipient_pop = Population.from_csv_file(
            analysis_params["recipient population file"], obj.sample_size
        )
        obj.num_bins = analysis_params["number bins"]
        obj.count_populations = bool(int(analysis_params["count populations"]))
        obj.combination_number = analysis_params["combination number"]

        return obj

    def perform_analysis(self):
        if self.combination_number == 1:
            for source_genome in self.source_pop.sample:
                for recipient_genome in self.recipient_pop.sample:
                    tree = Tree.initialized(
                        source_genome,
                        recipient_genome,
                        self.source_pop,
                        self.recipient_pop
                    )
                    self.collect_tree_results([tree])
        else:
            for _ in range(10_000):
                trees = []
                for c in range(self.combination_number):
                    source_genome = random.choice(self.source_pop.sample)
                    recipient_genome = random.choice(self.recipient_pop.sample)
                    tree = Tree.initialized(
                        source_genome,
                        recipient_genome,
                        self.source_pop,
                        self.recipient_pop
                    )
                    trees.append(tree)

                if len(trees) != self.combination_number:
                    raise ValueError(
                        "Number of trees not equal to combination number"
                    )
                self.collect_tree_results(trees)

    def collect_tree_results(self, trees):
        tier1 = self.collect_tier_1(trees)
        tier2 = self.collect_tier_2(trees)
        tally, magnitude = self.collect_clumpiness_composite(trees)

        tree_results = pd.DataFrame({
            'tier 1': [tier1],
            'tier 2': [tier2],
            'clumpiness tally': [tally],
            'clumpiness magnitude': [magnitude]
        })

        self.results = pd.concat([self.results, tree_results])

    def collect_tier_1(self, trees):
        tier_1_results = [tree.check_tier_1() for tree in trees]
        max_src_seg = max(
            map(lambda r: r["source segregating"], tier_1_results)
        )
        max_rec_seg = max(
            map(lambda r: r["recipient segregating"], tier_1_results)
        )

        if max_src_seg > max_rec_seg:
            return 1
        if max_src_seg < max_rec_seg:
            return -1
        return 0

    def collect_tier_2(self, trees):
        tier_2_results = [tree.check_tier_2() for tree in trees]
        max_src_on_rec = max(
            map(lambda r: r["source segregating on recipient"], tier_2_results)
        )
        max_rec_on_src = max(
            map(lambda r: r["recipient segregating on source"], tier_2_results)
        )

        if max_src_on_rec > max_rec_on_src:
            return 1
        if max_src_on_rec < max_rec_on_src:
            return -1
        return 0

    def collect_clumpiness_composite(self, trees):
        clumpiness_results = [
            tree.check_clumpiness_composite(self.num_bins) for tree in trees
        ]

        tally = {'correct': 0, 'reverse': 0}
        diff = {'source': [], 'recipient': []}
        for result in clumpiness_results:
            src_on_src = result["ancestral to source lineage"]["source"]
            rec_on_src = result["ancestral to source lineage"]["recipient"]
            rec_on_rec = result["ancestral to recipient lineage"]["recipient"]
            src_on_rec = result["ancestral to recipient lineage"]["source"]

            # tally
            if src_on_src > rec_on_src:
                if src_on_rec > rec_on_rec:
                    correct = 1
                    reverse = 0
                elif src_on_rec <= rec_on_rec:
                    correct = 0
                    reverse = 0
            elif src_on_src <= rec_on_src:
                if src_on_rec <= rec_on_rec:
                    correct = 0
                    reverse = 1
                elif src_on_rec > rec_on_rec:
                    correct = 0
                    reverse = 0

            tally['correct'] += correct
            tally['reverse'] += reverse

            # magnitude
            if rec_on_src == 0:
                rec_on_src = 1
                src_on_src += 100
            if rec_on_rec == 0:
                rec_on_rec = 1
                src_on_rec += 100
            diff['source'].append(src_on_src / rec_on_src)
            diff['recipient'].append(src_on_rec / rec_on_rec)

        # tally
        if tally['correct'] > tally['reverse']:
            tally = 1
        elif tally['correct'] < tally['reverse']:
            tally = -1
        else:
            tally = 0

        # magnitude
        source_diff = sum(diff['source']) / len(diff['source'])
        recipient_diff = sum(diff['recipient']) / len(diff['recipient'])
        if source_diff > 1:
            if recipient_diff > 1:
                magnitude = 1
            elif recipient_diff <= 1:
                magnitude = 0
        elif source_diff <= 1:
            if recipient_diff <= 1:
                magnitude = -1
            elif recipient_diff > 1:
                magnitude = 0

        return tally, magnitude
