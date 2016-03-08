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

    for cell in fm.cell_array.keys():
        nets = fm.cell_array.get(cell)
        for net in nets:
            assert cell in fm.net_array[net]

    for net in fm.net_array.keys():
        cells = fm.net_array.get(net)
        for cell in cells:
            assert net in fm.cell_array[cell]

    # for net in fm.net_array.keys():
    #     print("net %d: %s" % (net, ",".join([str(x) for x in fm.net_array[net]])))
    #
    # for cell in fm.cell_array.keys():
    #     print("cell %d: %s" % (cell, ",".join([str(x) for x in fm.cell_array[cell]])))

    assert fm.net_array[0] == {0, 1}
    assert fm.net_array[1] == {0, 2}
    assert fm.net_array[2] == {0, 4}
    assert fm.net_array[3] == {1, 2}
    assert fm.net_array[4] == {1, 3}
    assert fm.net_array[5] == {2, 4}
    assert fm.net_array[6] == {3, 4}

    assert fm.cell_array[0] == {0, 1, 2}
    assert fm.cell_array[1] == {0, 3, 4}
    assert fm.cell_array[2] == {1, 3, 5}
    assert fm.cell_array[3] == {4, 6}
    assert fm.cell_array[4] == {2, 5, 6}

