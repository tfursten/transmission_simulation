from ..Genome import Genome


class TestGenome:
  def test_eq_overload(self):
    assert Genome([]) == Genome([])
    assert Genome([]) != Genome([1])
    assert Genome([1,2,3]) == Genome([2,1,3])
    assert Genome([1,2,3]) != Genome([1,2])
    assert Genome([1]) in [Genome([]), Genome([1])]
    assert Genome([]) not in [Genome([1]), Genome([1,2])]

  def test_is_unique_in_population(self):
    pop = [
      g1 := Genome([1,2,3,4]),
      g2 := Genome([1,2,3,4,5]),
      Genome([1,2,3,4]),
    ]
    assert not g1.is_unique_in_population(pop)
    assert g2.is_unique_in_population(pop)