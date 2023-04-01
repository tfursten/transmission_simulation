import math

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

  # def check_clumpiness_ancestral(self, num_bins):
  #   source_entropy, recipient_entropy = \
  #     self.check_clumpiness("gini", self.shared_branch, num_bins).values()
  #   return {
  #     "correct detection": int(source_entropy > recipient_entropy),
  #     "reverse detection": int(recipient_entropy > source_entropy)
  #   }
  
  # def check_clumpiness_composite_averaged(self, num_bins):
  #   ancestral_to_source = self.shared_branch | self.source_branch
  #   ancestral_to_recipient = self.shared_branch | self.recipient_branch
  #   a_to_s_source_entropy, a_to_s_recipient_entropy = \
  #     self.check_clumpiness("gini", ancestral_to_source, num_bins).values()
  #   a_to_r_source_entropy, a_to_r_recipient_entropy = \
  #     self.check_clumpiness("gini", ancestral_to_recipient, num_bins).values()

  #   avg_source_entropy = (a_to_s_source_entropy + a_to_r_source_entropy) / 2
  #   avg_recipient_entropy = \
  #     (a_to_s_recipient_entropy + a_to_r_recipient_entropy) / 2

  #   return {
  #     "correct detection": int(avg_source_entropy > avg_recipient_entropy),
  #     "reverse detection": int(avg_recipient_entropy > avg_source_entropy)
  #   }

  def check_clumpiness_composite_gini(self, branch, num_bins):
    return self.check_clumpiness_composite(self, "gini", branch, num_bins)

  def check_clumpiness_composite_standard(self, branch, num_bins):
    return self.check_clumpiness_composite(self, "standard", branch, num_bins)

  def check_clumpiness_composite(self, method, num_bins):
    ancestral_to_source = self.shared_branch | self.source_branch
    ancestral_to_recipient = self.shared_branch | self.recipient_branch
    a_to_s_source_entropy, a_to_s_recipient_entropy = \
      self.check_clumpiness(method, ancestral_to_source, num_bins).values()
    a_to_r_source_entropy, a_to_r_recipient_entropy = \
      self.check_clumpiness(method, ancestral_to_recipient, num_bins).values()

    correct = (a_to_s_source_entropy > a_to_s_recipient_entropy) and \
              (a_to_r_source_entropy >= a_to_r_recipient_entropy)
    reverse = (a_to_s_recipient_entropy > a_to_s_source_entropy) and \
              (a_to_r_recipient_entropy >= a_to_r_source_entropy)

    return {
      "correct detection": int(correct),
      "reverse detection": int(reverse)
    }

  def check_clumpiness(self, method, branch, num_bins):
    source_proportions = [v["source_proportion"] for v in branch.values()]
    source_proportions_binned = \
      self.bin_proportions(source_proportions, num_bins) 
    recipient_proportions = [v["recipient_proportion"] for v in branch.values()] 
    recipient_proportions_binned = \
      self.bin_proportions(recipient_proportions, num_bins) 

    if method == "standard":
      source_entropy = self.standard_entropy(source_proportions_binned)
      recipient_entropy = self.standard_entropy(recipient_proportions_binned)
    elif method == "gini":
      source_entropy = self.gini_purity(source_proportions_binned)
      recipient_entropy = self.gini_purity(recipient_proportions_binned)
    else:
      raise ValueError("expected 'standard' or 'gini' entropy method")

    return {
      "source entropy": source_entropy,
      "recipient entropy": recipient_entropy
    }

  def bin_proportions(self, proportions, num_bins):
    # note: having a bin number greater than the sample size is pointless
    # because proportions can only vary in increments as small as 
    # 1 / sample size
    if not proportions or not num_bins:
      return []

    import math
    bin_size = 1 / num_bins

    # bins: [ [a, b], (b, c], (c, d], ... ]
    # note that lowest bin is double inclusive to include 0
    proportions_by_bin_index = []
    for proportion in proportions:
      if proportion == 0:
        proportions_by_bin_index.append(0)
      else:
        index = math.ceil(proportion / bin_size) - 1
        proportions_by_bin_index.append(index)

    return [proportions_by_bin_index.count(bin) for bin in range(num_bins)]

  def gini_purity(self, binned_proportions):
    if len(binned_proportions) <= 1 or sum(binned_proportions) == 1:
      return 0

    max = (sum(binned_proportions) ** 2) - sum(binned_proportions)
    entropy = sum([((p ** 2) - p) for p in binned_proportions]) / max 
    return 1 - entropy
  
  def standard_entropy(self, binned_proportions):
    if len(binned_proportions) <= 1 or sum(binned_proportions):
      return 0

    props = [p / sum(binned_proportions) for p in binned_proportions]
    return sum([p * math.log(p) if p > 0 else 0 for p in props]) * -1
  
   

    