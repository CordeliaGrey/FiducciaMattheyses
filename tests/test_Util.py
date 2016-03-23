from Util import *
from FiducciaMattheyses import FiducciaMattheyses
from tests.test_FiducciaMattheyses import assert_block

__author__ = 'gm'


def test_bucket_array():
    pmax = 5
    fm = FiducciaMattheyses()
    fm.blockA = Block("A", pmax, fm)
    fm.blockB = Block("B", pmax, fm)

    ba = fm.blockA.bucket_array

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

    #
    # this happens automatically in input routine, do it manually here
    #
    c1.block = fm.blockA
    c2.block = fm.blockA
    c3.block = fm.blockA

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

    assert c1 in ba[c1.gain]
    ba2 = BucketArray(pmax)
    assert c1.locked is False
    c1.gain = 3
    ba.yank_cell(c1)
    assert c1.locked is False

    assert len(ba[1]) == 1
    assert len(ba[3]) == 1
    assert c1.gain == 3
    assert ba.max_gain == 5
    assert ba.get_candidate_base_cell() == c3

    assert c3.locked is False
    c3.gain = 4
    ba.yank_cell(c3)
    assert c3.locked is False
    assert c3.gain == 4
    assert ba.max_gain == 4
    assert ba.get_candidate_base_cell() == c3

    ba.remove_cell(c3)
    assert ba.max_gain == 3
    assert len(ba[4]) == 0

    assert ba.get_candidate_base_cell() == c1


def test_cell_net():
    pmax = 5
    fm = FiducciaMattheyses()
    fm.blockA = Block("A", pmax, fm)
    fm.blockB = Block("B", pmax, fm)

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

    #
    # this happens automatically in input routine, do it manually here
    #
    c1.block = fm.blockA
    c2.block = fm.blockA
    c3.block = fm.blockA

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

    assert c2.locked is False
    assert all(net.blockA_locked == 0 for net in c2.nets)
    assert all(net.blockA_free == 2 for net in c2.nets)
    c2.lock()
    assert c2.locked is True
    assert all(net.blockA_locked == 1 for net in c2.nets)
    assert all(net.blockA_free == 1 for net in c2.nets)
    c3.lock()
    assert all(net.blockA_locked == 2 or net.n != 1 for net in c2.nets)
    assert all(net.blockA_free == 0 or net.n != 1 for net in c2.nets)
    c3.unlock()
    c2.unlock()
    assert all(net.blockA_locked == 0 for net in c2.nets)
    assert all(net.blockA_free == 2 for net in c2.nets)


def test_block():
    pmax = 5
    fm = FiducciaMattheyses()
    fm.pmax = 5
    fm.blockA = Block("A", pmax, fm)
    fm.blockB = Block("B", pmax, fm)

    c1 = Cell(0, "A")
    c1.gain = -1

    c2 = Cell(1, "A")
    c2.gain = -2

    c3 = Cell(2, "A")
    c3.gain = -1

    n1 = Net(0)
    n1.add_cell(c1)
    n1.add_cell(c2)
    n1.blockA_ref = fm.blockA
    n2 = Net(1)
    n2.blockA_ref = fm.blockA
    n2.add_cell(c2)
    n2.add_cell(c3)

    c1.add_net(n1)
    c2.add_net(n1)
    c2.add_net(n2)
    c3.add_net(n2)

    #
    # this happens automatically in input routine, do it manually here
    #
    c1.block = fm.blockA
    c2.block = fm.blockA
    c3.block = fm.blockA
    n1.blockA_ref = fm.blockA
    n1.blockB_ref = fm.blockB
    n2.blockA_ref = fm.blockA
    n2.blockB_ref = fm.blockB

    b = fm.blockA
    b.add_cell(c1)
    b.add_cell(c2)
    b.add_cell(c3)

    for c in n1.cells:
        c.lock()
    for c in n2.cells:
        c.lock()
    b.initialize()

    assert_block(b, fm)

    assert b.size == 3
    assert len(b.bucket_array[-1]) == 2
    assert len(b.bucket_array[-2]) == 1
    assert b.get_candidate_base_cell() == c1

    b2 = fm.blockB

    assert n1.blockA == 2
    assert n1.blockB == 0
    assert len(n1.blockA_cells) == 2
    assert n1.blockA_cells == [c1, c2]
    assert n1.blockA_free == 2
    assert n1.blockA_locked == 0
    assert fm.cutset == 0
    assert len(b.bucket_array[-1]) == 2
    b.move_cell(c1)
    assert fm.cutset == 1

    assert_block(b, fm)
    assert_block(b2, fm)

    assert b.size == 2
    assert b2.size == 1

    b2.initialize()
    assert len(b2.bucket_array[c1.gain]) == 1


def test_snapshots():
    pmax = 5
    fm = FiducciaMattheyses()
    fm.pmax = 5
    fm.blockA = Block("A", pmax, fm)
    fm.blockB = Block("B", pmax, fm)

    c1 = Cell(0, "A")
    c1.gain = -1

    c2 = Cell(1, "A")
    c2.gain = -2

    c3 = Cell(2, "A")
    c3.gain = -1

    n1 = Net(0)
    n1.add_cell(c1)
    n1.add_cell(c2)
    n1.blockA_ref = fm.blockA
    n2 = Net(1)
    n2.blockA_ref = fm.blockA
    n2.add_cell(c2)
    n2.add_cell(c3)

    c1.add_net(n1)
    c2.add_net(n1)
    c2.add_net(n2)
    c3.add_net(n2)

    #
    # this happens automatically in input routine, do it manually here
    #
    c1.block = fm.blockA
    c2.block = fm.blockA
    c3.block = fm.blockA
    n1.blockA_ref = fm.blockA
    n1.blockB_ref = fm.blockB
    n2.blockA_ref = fm.blockA
    n2.blockB_ref = fm.blockB

    b = fm.blockA
    b.add_cell(c1)
    b.add_cell(c2)
    b.add_cell(c3)

    assert_block(fm.blockA, fm)
    assert_block(fm.blockB, fm)

    fm.blockA.initialize()

    # c1.take_snapshot()
    # c1.load_snapshot()
    # n1.take_snapshot()
    # n1.load_snapshot()
    # fm.blockA.take_snapshot()
    # fm.blockA.load_snapshot()
    fm.take_snapshot()
    fm.load_snapshot()

    assert_block(fm.blockA, fm)
    assert_block(fm.blockB, fm)

    fm.blockA.move_cell(c1)
    fm.blockA.move_cell(c3)

    fm.blockB.initialize()

    assert_block(fm.blockA, fm)
    assert_block(fm.blockB, fm)

    fm.take_snapshot()
    fm.load_snapshot()

    fm.blockA.move_cell(c2)

    fm.take_snapshot()
    fm.load_snapshot()

    fm.blockB.move_cell(c1)

    fm.take_snapshot()
    fm.load_snapshot()

    fm.blockB.move_cell(c3)

    fm.take_snapshot()
    fm.load_snapshot()

    fm.blockA.initialize()

    fm.take_snapshot()
    fm.load_snapshot()

    fm.blockB.initialize()

    assert_block(fm.blockA, fm)
    assert_block(fm.blockB, fm)

    assert True
