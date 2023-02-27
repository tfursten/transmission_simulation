class Tree:
  def __init__(self):
    self.source_genome = None
    self.recipient_genome = None
    self.source_population = None
    self.recipient_population = None
    self.shared_branch = {}
    self.source_branch = {}
    self.recipient_branch = {}

  @classmethod
  def initialized(cls, source_genome, recipient_genome, source_population, 
                  recipient_population):
    obj = cls()
    obj.source_genome = source_genome
    obj.recipient_genome = recipient_genome
    obj.source_population = source_population
    obj.recipient_population = recipient_population

    # branches: 
    # {
    #   mutation: {
    #    source_proportion: _
    #    recipient_proportion: _ 
    #   },
    # }
    obj.categorize_mutations() 
    obj.assign_proportions()

    return obj

  def categorize_mutations(self):
    for mutation in self.source_genome.mutations:
      if mutation in self.recipient_genome.mutations:
        self.shared_branch[mutation] = {}
      else:
        self.source_branch[mutation] = {}

    for mutation in self.recipient_genome.mutations:
      if mutation not in self.source_genome.mutations:
        self.recipient_branch[mutation] = {}
    
  def assign_proportions(self):
    for branch in self.shared_branch, self.source_branch, self.recipient_branch:
      for mutation in branch:
        if mutation in (src_snps := self.source_population.sample_snps): 
          branch[mutation]["source_proportion"] = \
            src_snps[mutation]["proportion"]
        else:
          branch[mutation]["source_proportion"] = 0

        if mutation in (rec_snps := self.recipient_population.sample_snps): 
          branch[mutation]["recipient_proportion"] = \
            rec_snps[mutation]["proportion"]
        else:
          branch[mutation]["recipient_proportion"] = 0
  
  def count_segregating_snps(self, population, branch):
    segs = 0
    for mutation in branch:
      proportion = branch[mutation][population + "_proportion"]    
      if proportion < 1 and proportion > 0:
        segs += 1
    
    return segs

  def check_tier_1(self):
    src_segregating = self.count_segregating_snps("source", self.shared_branch) 
    rec_segregating = \
      self.count_segregating_snps("recipient", self.shared_branch)

    correct = int(src_segregating > rec_segregating)
    reverse = int(rec_segregating > src_segregating)
    return {
      "correct detection": correct,
      "reverse detection": reverse
    }

  def check_tier_2(self):
    src_on_rec_branch_segs = \
      self.count_segregating_snps("source", self.recipient_branch)
    rec_on_src_branch_segs = \
      self.count_segregating_snps("recipient", self.source_branch) 

    correct = int(src_on_rec_branch_segs > 0 and rec_on_src_branch_segs == 0) 
    reverse = int(rec_on_src_branch_segs > 0 and src_on_rec_branch_segs == 0)
    return {
      "correct detection": correct,
      "reverse detection": reverse
    }

  def compare_clumpiness(self, branch, num_bins=10):
    source_proportions = [v["source_proportion"] for v in branch.values()]
    source_proportions_binned = \
      self.bin_proportions(source_proportions, num_bins) 
    recipient_proportions = [v["recipient_proportion"] for v in branch.values()] 
    recipient_proportions_binned = \
      self.bin_proportions(recipient_proportions, num_bins) 

    source_entropy = self.psuedo_entropy(source_proportions_binned)
    recipient_entropy = self.psuedo_entropy(recipient_proportions_binned)

    correct = int(source_entropy > recipient_entropy)
    reverse = int(recipient_entropy > source_entropy)
    return {
      "correct detection": correct,
      "reverse detection": reverse
    }

  def bin_proportions(self, proportions, num_bins):
    # note: having a bin number greater than the sample size is pointless
    # because proportions can only vary in increments as small as 
    # 1 / sample size
    if not proportions or not num_bins:
      return []

    import math
    bin_size = 1 / num_bins # proportions range (0, 1]

    # note: need to handle 0 proportions for divergent branches...
    # bins: [ (a, b], (b, c], ... ]
    props_by_bin = [math.ceil(prop / bin_size) - 1  for prop in proportions]
    return [props_by_bin.count(bin) for bin in range(num_bins)]
  
  def psuedo_entropy(self, binned_proportions):
    if len(binned_proportions) <= 1 or sum(binned_proportions) == 1:
      return 0

    max = (sum(binned_proportions) ** 2) - sum(binned_proportions)
    entropy = sum([((prop ** 2) - prop) for prop in binned_proportions]) / max 
    return 1 - entropy

    