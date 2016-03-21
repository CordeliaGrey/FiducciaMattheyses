from Util import *

__author__ = 'gm'


def test_Util():

    pmax = 5
    ba = BucketArray(pmax)

    assert len(ba.array) == 11
    assert ba.max_gain == -5

    c1 = Cell(0, "A")
    c1.gain = 1
    c1.nets = 1
    c1.pins = 1

    c2 = Cell(1, "A")
    c2.gain = 1
    c2.nets = 1
    c2.pins = 1

    c3 = Cell(2, "A")
    c3.gain = 5
    c3.nets = 1
    c3.pins = 1

    assert len(ba[1]) == 0

    ba.add_cell(c1)

    assert len(ba.array) == 11
    assert ba.max_gain == 1
    assert len(ba[1]) == 1
    assert len(ba[-2]) == 0
    assert len(ba[-4]) == 0
    assert ba[1][0].n == 0
    assert ba[1][0].gain == 1
    assert ba[1][0].nets == 1
    assert ba[1][0].pins == 1
    assert ba.get_candidate_base_cell() == c1

    ba.add_cell(c2)

    assert len(ba.array) == 11
    assert ba.max_gain == 1
    assert len(ba[1]) == 2
    assert ba[1][0].n == 0
    assert ba[1][1].n == 1
    assert ba.get_candidate_base_cell() == c1

    ba.add_cell(c3)

    assert len(ba.array) == 11
    assert ba.max_gain == 5
    assert len(ba[1]) == 2
    assert ba[1][0].n == 0
    assert ba[1][1].n == 1
    assert ba.get_candidate_base_cell() == c3

    assert len(ba.free_cell_list) == 0
    assert c1 in ba[c1.gain]
    ba2 = BucketArray(pmax)
    assert c1.locked is False
    ba.move_cell(c1, 3, ba2)
    assert c1.locked is True

    assert len(ba.free_cell_list) == 0
    assert len(ba2.free_cell_list) == 1
    assert len(ba[1]) == 1
    assert c1.gain == 3
    assert ba.max_gain == 5
    assert ba.get_candidate_base_cell() == c3

    assert c3.locked is False
    ba.move_cell(c3, 0, ba2)
    assert c3.locked is True
    assert len(ba2.free_cell_list) == 2
    assert c3.gain == 0
    assert ba.max_gain == 1
    assert ba.get_candidate_base_cell() == c2
