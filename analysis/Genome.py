class Genome:
  __slots__ = "mutations"

  def __init__(self, mutations):
    self.mutations = mutations
  
  def __eq__(self, other):
    return sorted(self.mutations) == sorted(other.mutations)
  
  def is_unique_in_population(self, population):
    self_counted = False # genome is in its own population
    for genome in population:
      if genome == self:
        if self_counted:
          return False
        self_counted = True

    return True
  