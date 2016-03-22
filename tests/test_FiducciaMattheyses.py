import numpy as np
from FiducciaMattheyses import FiducciaMattheyses

__author__ = 'gm'


def test_input_routine():
    PM = [[1, 1, 1, 0, 1],
          [1, 1, 1, 1, 0],
          [1, 1, 1, 0, 1],
          [0, 1, 0, 1, 1],
          [1, 0, 1, 1, 1]]

    PM = np.array(PM, dtype="b1", order='C')

    fm = FiducciaMattheyses()
    fm.input_routine(PM)

    for cell in fm.cell_array.values():
        for net in cell.nets:
            assert cell in net.cells

    for net in fm.net_array.values():
        for cell in net.cells:
            assert net in cell.nets

    # for net in fm.net_array.keys():
    #     print("net %d: %s" % (net, ",".join([str(x.n) for x in fm.net_array[net].cells])))
    #
    # for cell in fm.cell_array.keys():
    #     print("cell %d: %s" % (cell, ",".join([str(x.n) for x in fm.cell_array[cell].nets])))

    assert {0, 1} == set(x.n for x in fm.net_array[0].cells)
    assert {0, 2} == set(x.n for x in fm.net_array[1].cells)
    assert {0, 4} == set(x.n for x in fm.net_array[2].cells)
    assert {1, 2} == set(x.n for x in fm.net_array[3].cells)
    assert {1, 3} == set(x.n for x in fm.net_array[4].cells)
    assert {2, 4} == set(x.n for x in fm.net_array[5].cells)
    assert {3, 4} == set(x.n for x in fm.net_array[6].cells)

    assert {0, 1, 2} == set(x.n for x in fm.cell_array[0].nets)
    assert {0, 3, 4} == set(x.n for x in fm.cell_array[1].nets)
    assert {1, 3, 5} == set(x.n for x in fm.cell_array[2].nets)
    assert {4, 6} == set(x.n for x in fm.cell_array[3].nets)
    assert {2, 5, 6} == set(x.n for x in fm.cell_array[4].nets)

    assert fm.pmax == 3

    assert fm.net_array[0].blockA == 2
    assert fm.net_array[1].blockA == 2
    assert fm.net_array[2].blockA == 2
    assert fm.net_array[3].blockA == 2
    assert fm.net_array[4].blockA == 2
    assert fm.net_array[5].blockA == 2
    assert fm.net_array[6].blockA == 2

    assert all(net.blockA_locked == 0 for net in fm.net_array.values())
    assert all(net.blockA_free == net.blockA for net in fm.net_array.values())



def test_compute_initial_gains():
    PM = [[1, 1, 1, 0, 1],
          [1, 1, 1, 1, 0],
          [1, 1, 1, 0, 1],
          [0, 1, 0, 1, 1],
          [1, 0, 1, 1, 1]]

    PM = np.array(PM, dtype="b1", order='C')

    fm = FiducciaMattheyses()
    fm.input_routine(PM)

    fm.compute_initial_gains()

    assert fm.cell_array[0].gain == -3
    assert fm.cell_array[1].gain == -3
    assert fm.cell_array[2].gain == -3
    assert fm.cell_array[3].gain == -2
    assert fm.cell_array[4].gain == -3


def test_initial_pass():
    PM = [[1, 1, 1, 0, 1],
          [1, 1, 1, 1, 0],
          [1, 1, 1, 0, 1],
          [0, 1, 0, 1, 1],
          [1, 0, 1, 1, 1]]

    PM = np.array(PM, dtype="b1", order='C')

    fm = FiducciaMattheyses()
    fm.input_routine(PM)

    assert fm.cutset == 0
    fm.initial_pass()
    assert fm.cutset != 0

    assert len(fm.blockA.cells) == fm.blockA.size
    assert len(fm.blockB.cells) == fm.blockB.size

    assert len(fm.blockA.bucket_array.free_cell_list) == 0
    assert len(fm.blockB.bucket_array.free_cell_list) == 0

    assert all(cell.locked is False for cell in fm.cell_array.values())

    print(fm.blockA.size)
    print(fm.blockB.size)

    # assert False


def test_perform_pass():
    PM = [[1, 1, 1, 0, 1],
          [1, 1, 1, 1, 0],
          [1, 1, 1, 0, 1],
          [0, 1, 0, 1, 1],
          [1, 0, 1, 1, 1]]

    PM = np.array(PM, dtype="b1", order='C')

    fm = FiducciaMattheyses()
    fm.input_routine(PM)
    fm.initial_pass()
    fm.perform_pass()

    assert True