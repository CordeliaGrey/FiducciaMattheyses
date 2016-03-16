import numpy as np

__author__ = 'gm'


class FiducciaMattheyses:
    def __init__(self):
        self.cell_array = {}
        self.net_array = {}

    def input_routine(self, correlation_matrix: np.ndarray):
        """
        constructs the cell_array and net_array from an input matrix of the form
        [[1, 1, 1, 0, 1],
         [1, 1, 1, 1, 0],
         [1, 1, 1, 0, 1],
         [0, 1, 0, 1, 1],
         [1, 0, 1, 1, 1]]
        where 1 represents an edge between two nodes.
        In the above example node 0 is connected to 1, 2 and 4 (by looking at the first line of the table)
        """
        assert isinstance(correlation_matrix, np.ndarray)
        I, J = correlation_matrix.shape
        net = 0
        for i in range(I):
            for j in range(i+1, J):
                if correlation_matrix[i][j] == 1:
                    self.__add_to_cell_array(i, net)
                    self.__add_to_net_array(net, i)
                    self.__add_to_cell_array(j, net)
                    self.__add_to_net_array(net, j)
                    net += 1

    def __add_to_cell_array(self, cell: int, net: int):
        """
        adds given cell to cell_array if it does not exist and net to this cell's net list
        """
        if cell not in self.cell_array:
            self.cell_array[cell] = {net}
        else:
            self.cell_array[cell].add(net)

    def __add_to_net_array(self, net: int, cell: int):
        """
        adds given net to net_array if it does not exists and cell to this net's cell list
        """
        if net not in self.net_array:
            self.net_array[net] = {cell}
        else:
            self.net_array[net].add(cell)


class Cell:
    def __init__(self, n: int):
        assert n >= 0
        self.n = n      # the cell number
        self.pins = 0   # number of nets
        self.nets = []  # nets that this cell is part of
        self.gain = 0   # the gain of this cell

