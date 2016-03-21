from Util import *

__author__ = 'gm'


def test_bucket_array():

    pmax = 5
    ba = BucketArray(pmax)

    assert len(ba.array) == 11
    assert ba.max_gain == -5

    n = Net(0)
    c1 = Cell(0, "A")
    c1.gain = 1
    c1.add_net(n)

    c2 = Cell(1, "A")
    c2.gain = 1
    c2.add_net(n)

    c3 = Cell(2, "A")
    c3.gain = 5
    c3.add_net(n)

    n.add_cell(c1)
    n.add_cell(c2)
    n.add_cell(c3)

    assert len(ba[1]) == 0

    ba.add_cell(c1)

    assert len(ba.array) == 11
    assert ba.max_gain == 1
    assert len(ba[1]) == 1
    assert len(ba[-2]) == 0
    assert len(ba[-4]) == 0
    assert ba[1][0].n == 0
    assert ba[1][0].gain == 1
    assert len(ba[1][0].nets) == 1
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

    assert len(ba2[0]) == 0
    assert len(ba2[3]) == 0
    ba2.initialize()
    assert len(ba2[0]) == 1
    assert len(ba2[3]) == 1


def test_cell_net():
    c1 = Cell(0, "A")
    c1.gain = -1

    c2 = Cell(1, "A")
    c2.gain = -2

    c3 = Cell(2, "A")
    c3.gain = -1

    n1 = Net(0)
    n1.add_cell(c1)
    n1.add_cell(c2)
    n2 = Net(1)
    n2.add_cell(c2)
    n2.add_cell(c3)

    c1.add_net(n1)
    c2.add_net(n1)
    c2.add_net(n2)
    c3.add_net(n2)

    assert len(c1.nets) == 1
    assert len(c2.nets) == 2
    assert len(c3.nets) == 1

    assert len(n1.cells) == 2
    assert len(n2.cells) == 2

    assert n1.n == 0
    assert n1.blockA == 2
    assert n1.blockB == 0
    assert n2.n == 1
    assert n2.blockA == 2
    assert n2.blockB == 0


def test_block():
    pmax = 5

    c1 = Cell(0, "A")
    c1.gain = -1

    c2 = Cell(1, "A")
    c2.gain = -2

    c3 = Cell(2, "A")
    c3.gain = -1

    n1 = Net(0)
    n1.add_cell(c1)
    n1.add_cell(c2)
    n2 = Net(1)
    n2.add_cell(c2)
    n2.add_cell(c3)

    c1.add_net(n1)
    c2.add_net(n1)
    c2.add_net(n2)
    c3.add_net(n2)

    b = Block("A", pmax)
    b.add_cell(c1)
    b.add_cell(c2)
    b.add_cell(c3)

    b.initialize()

    assert b.size == 3
    assert len(b.bucket_array[-1]) == 2
    assert len(b.bucket_array[-2]) == 1
    assert b.get_candidate_base_cell() == c1

    b2 = Block("B", pmax)

    b.move_cell(c1, b2)

    assert b.size == 2
    assert b2.size == 1
    assert len(b.bucket_array[-1]) == 1
