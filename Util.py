__author__ = 'gm'


class Cell:
    def __init__(self, n: int, block):
        assert n >= 0
        assert isinstance(block, Block)
        self.n = n  # the cell number
        self.pins = 0  # number of nets
        self.nets = set()  # nets that this cell is part of
        self.gain = 0  # the gain of this cell
        self.block = block  # the block this cell belongs to

    def add_net(self, net):
        self.nets.add(net)
        self.pins += 1


class Net:
    def __init__(self, n: int):
        assert n >= 0
        self.n = n  # the net number
        self.cells = set()  # the cells that this net contains
        self.blockA = 0  # the number of cells in this net that belong to bock A
        self.blockB = 0  # the number of cells in this net that belong to bock B

    def add_cell(self, cell):
        self.cells.add(cell)


class Block:
    def __init__(self, pmax):
        self.size = 0
        self.bucket_array = BucketArray(pmax)


class BucketArray:
    def __init__(self, pmax):
        self.max_gain = -pmax
        self.pmax = pmax
        self.array = [[] for x in range(pmax * 2 + 1)]
        self.free_cell_list = []

    def __getitem__(self, i: int) -> list:
        assert -self.pmax <= i <= self.pmax
        i += self.pmax
        return self.array[i]

    def move_cell(self, cell: Cell, to_gain: int, bucket_array):
        """
        move a cell from its bucket list to the free cell list of some other bucket array, also adjusting its gain
        """
        assert isinstance(cell, Cell)
        assert isinstance(to_gain, int)
        assert isinstance(bucket_array, BucketArray)

        assert -self.pmax <= cell.gain <= self.pmax
        assert -self.pmax <= to_gain <= self.pmax
        self[cell.gain].remove(cell)
        if len(self[cell.gain]) == 0:
            self.decrement_max_gain()
        cell.gain = to_gain
        bucket_array.add_to_free_cell_list(cell)

    def decrement_max_gain(self):
        """
        decrements max gain by 1. If the bucket array in that index is empty max gain is decremented by 1 again,
        this is repeated until max gain reaches -pmax or a bucket array that is not empty
        """
        while self.max_gain > -self.pmax:
            self.max_gain -= 1
            if len(self[self.max_gain]) != 0:
                break

    def add_cell(self, cell: Cell):
        """
        add a cell to the appropriate bucket list, depending on its gain. Adjust max gain index appropriately
        """
        assert isinstance(cell, Cell)
        assert -self.pmax <= cell.gain <= self.pmax

        self[cell.gain].append(cell)
        if cell.gain > self.max_gain:
            self.max_gain = cell.gain

    def add_to_free_cell_list(self, cell: Cell):
        """
        puts the cell to the free cell list of this BucketArray, keep locked cells here until reinitialization
        """
        assert isinstance(cell, Cell)
        self.free_cell_list.append(cell)
