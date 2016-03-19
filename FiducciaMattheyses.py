import numpy as np
from Util import Cell, Net

__author__ = 'gm'


class FiducciaMattheyses:
    INITIAL_BLOCK = "A"

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
                    self.__add_pair(i, j, net)
                    net += 1

    def __add_pair(self, i: int, j: int, net_n: int):
        """
        add a connected pair of nodes. Adds cell_i, cell_j, net if they do not already exist to cell_array and
        net array accordingly. Also adds dependencies between the cells and the net
        """
        cell_i = self.__add_cell(i)
        cell_j = self.__add_cell(j)
        net = self.__add_net(net_n)

        cell_i.add_net(net)
        cell_j.add_net(net)
        net.add_cell(cell_i)
        net.add_cell(cell_j)

    def __add_cell(self, cell: int) -> Cell:
        """
        add a cell to the cell_array if it does not exist, return the new cell created or the existing one
        """
        if cell not in self.cell_array:
            cell_obj = Cell(cell, FiducciaMattheyses.INITIAL_BLOCK)
            self.cell_array[cell] = cell_obj
        else:
            cell_obj = self.cell_array[cell]
        return cell_obj

    def __add_net(self, net: int) -> Net:
        """
        add a net to the net_array if it does not exist, return the new net created or the existing one
        """
        if net not in self.net_array:
            net_obj = Net(net)
            self.net_array[net] = net_obj
        else:
            net_obj = self.net_array[net]
        return net_obj

