import numpy as np
from Util import Cell, Net, Block

__author__ = 'gm'


class FiducciaMattheyses:
    INITIAL_BLOCK = "A"  # block that all cells initially belong to
    r = 0.5  # ratio intended to capture the balance criterion of the final partition produced by the algorithm

    def __init__(self):
        self.cell_array = {}
        self.net_array = {}
        self.pmax = 0  # this gets calculated in input_routine

        self.blockA = None  # this gets initialized when input routine is called (we need to know pmax)
        """:type blockA Block"""
        self.blockB = None  # this gets initialized when input routine is called (we need to know pmax)
        """:type blockB Block"""

    def input_routine(self, edge_matrix: np.ndarray):
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
        assert isinstance(edge_matrix, np.ndarray)
        I, J = edge_matrix.shape
        net = 0
        for i in range(I):
            for j in range(i + 1, J):
                if edge_matrix[i][j] == 1:
                    self.__add_pair(i, j, net)
                    net += 1

        for cell in self.cell_array.values():
            if cell.pins > self.pmax:
                self.pmax = cell.pins

        self.blockA = Block("A", self.pmax)
        self.blockB = Block("B", self.pmax)

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

    def get_base_cell(self):
        """
        get the base cell. That is a cell with maximum gain that also gives the best balance if moved to its
        complementary block
        """
        a = self.get_candidate_base_cell_from_block(self.blockA)
        b = self.get_candidate_base_cell_from_block(self.blockB)

        if a is None and b is None:
            return None
        elif a is None and b is not None:
            return b
        elif a is not None and b is None:
            return a
        else:  # both not None
            bfactor_a = a[1]
            bfactor_b = b[1]
            if bfactor_a < bfactor_b:
                return a[0]
            else:
                return a[1]

    def get_candidate_base_cell_from_block(self, block: Block):  # -> Tuple[Cell, float]
        """
        get a cell from the specified block that fulfills the requirements to be a base cell, or None if there
        is no such cell in the given block
        """
        assert isinstance(block, Block)
        candidate_cell = block.get_candidate_base_cell()
        if candidate_cell is None:
            return None
        bfactor = self.get_balance_factor(candidate_cell)
        if bfactor is None:
            return None
        else:
            return candidate_cell, bfactor

    def get_balance_factor(self, cell: Cell):
        """
        Using the balance criterion first check if moving this cell to the complementary block would result in a
        balance partition, if this is the case return abs(|A| - rW), else None. The closer this value is to zero
        the closer the partition is to the expected (based on ratio r)
        """
        if cell.block == "A":
            A = self.blockA.size - 1
            B = self.blockB.size + 1
        else:
            assert cell.block == "B"
            A = self.blockA.size + 1
            B = self.blockB.size - 1
        W = A + B
        smax = self.pmax
        r = FiducciaMattheyses.r
        if r * W - smax <= A <= r * W + smax:
            return abs(A - r * W)
        else:
            return None

    def is_partition_balanced(self) -> bool:
        """
        check the balance criterion and return true if the current partition is balanced
        """
        W = self.blockA.size + self.blockB.size
        smax = self.pmax
        r = FiducciaMattheyses.r
        A = self.blockA.size
        return r * W - smax <= A <= r * W + smax

    def move_cell(self, cell: Cell):
        """
        move the given cell to its complementary block
        """
        # TODO implement
        pass

    def initial_pass(self):
        """
        initial pass to establish a balanced partition
        """
        assert self.blockA is not None
        assert self.blockB is not None
        for cell in self.cell_array.values():
            if self.is_partition_balanced():
                break
            assert cell.block == "A"  # all cells initially belong to block A
            self.blockA.move_cell(cell, self.blockB)
