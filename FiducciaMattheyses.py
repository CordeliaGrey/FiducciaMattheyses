import numpy as np
from Util import Cell, Net, Block
import copy

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
        self.cutset = 0  # number of sets that are cut

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

        self.blockA = Block("A", self.pmax, self)
        self.blockB = Block("B", self.pmax, self)

        for cell in self.cell_array.values():
            self.blockA.add_cell(cell)
        for net in self.net_array.values():
            net.blockA_ref = self.blockA
            net.blockB_ref = self.blockB
        self.compute_initial_gains()
        self.blockA.initialize()

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

    def get_base_cell(self) -> Cell:
        """
        get the base cell. That is a cell with maximum gain that also gives the best balance if moved to its
        complementary block or null if no such cell exists
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
                return b[0]

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
        smax = 1  # self.pmax
        r = FiducciaMattheyses.r
        A = self.blockA.size
        return r * W - smax <= A <= r * W + smax

    def compute_initial_gains(self):
        """
        computes initial gains for all free cells, assumes that all cells initially belong to block A and are all free
        """
        for cell in self.cell_array.values():
            assert cell.block == "A"
            assert cell.locked is False
            cell.gain = 0
            for net in cell.nets:
                # FROM block is "A" since all cells initially belong to "A"
                if net.blockA == 1:
                    cell.gain += 1
                if net.blockB == 0:
                    cell.gain -= 1

    def initial_pass(self):
        """
        initial pass to establish a balanced partition, input_routine should have been called first
        """
        assert self.blockA is not None
        assert self.blockB is not None

        self.compute_initial_gains()

        assert self.blockA.size >= self.blockB.size
        while not self.is_partition_balanced():
            bcell = self.blockA.get_candidate_base_cell()
            assert bcell.block == "A"  # all cells initially belong to block A
            self.blockA.move_cell(bcell, self.blockB)
        self.blockB.initialize()

    def perform_pass(self):
        """
        perform a full pass, until no more cells are able to move or the balance criterion does not let any more moves.
        the input_routine() and initial_pass() functions must have been called first
        """
        best_cutset = 999999999999
        best_cell_array = {}
        best_net_array = {}
        best_blockA = None
        best_blockB = None
        bcell = self.get_base_cell()
        while bcell is not None:
            if bcell.block == "A":
                self.blockA.move_cell(bcell, self.blockB)
            else:
                assert bcell.block == "B"
                self.blockB.move_cell(bcell, self.blockA)
            if self.cutset < best_cutset:
                best_cutset = self.cutset
                best_cell_array = copy.deepcopy(self.cell_array)
                best_net_array = copy.deepcopy(self.net_array)
                best_blockA = copy.deepcopy(self.blockA)
                best_blockB = copy.deepcopy(self.blockB)
            bcell = self.get_base_cell()
        return best_cutset, best_cell_array, best_net_array, best_blockA, best_blockB


    def find_mincut(self):
        """
        perform multiple passes until no more improvements are given, keep the best pass
        """
