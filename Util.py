__author__ = 'gm'


class Cell:
    def __init__(self, n: int, block: str):
        assert n >= 0
        assert isinstance(block, str)
        assert block == "A" or block == "B"
        self.n = n  # the cell number
        self.pins = 0  # number of nets
        self.nets = set()  # nets that this cell is part of
        self.gain = 0  # the gain of this cell
        self.block = block  # the block this cell belongs to, "A" or "B"
        self.locked = False  # whether this cell locked or free to move

    def add_net(self, net):
        if net not in self.nets:
            self.nets.add(net)
            self.pins += 1

    def adjust_net_distribution(self):
        """
        call this after the cell moved to its complementary block, to adjust each nets distribution (each net that
        contains this cell)
        """
        for net in self.nets:
            if self.block == "A":  # "A" after move, so the cell moved to "A"
                net.cell_to_blockA()
            else:
                assert self.block == "B"  # "B" after move, so the cell moved to "B"
                net.cell_to_blockB()

    def lock(self):
        self.locked = True

    def unlock(self):
        self.locked = False


class Net:
    def __init__(self, n: int):
        assert n >= 0
        self.n = n  # the net number
        self.cells = set()  # the cells that this net contains
        self.blockA = 0  # the number of cells in this net that belong to bock A
        self.blockB = 0  # the number of cells in this net that belong to bock B

    def add_cell(self, cell):
        """
        add a cell to this net, increment blockA or blockB numbers depending on what block the added cell belongs to
        """
        if cell not in self.cells:
            self.cells.add(cell)
            if cell.block == "A":
                self.blockA += 1
            else:
                assert cell.block == "B"
                self.blockB += 1

    def cell_to_blockA(self):
        """
        call this when a cell moved to blockA, increments blockA and decrements blockB
        """
        self.blockA += 1
        self.blockB -= 1
        assert self.blockA >= 0
        assert self.blockB >= 0

    def cell_to_blockB(self):
        """
        call this when a cell moved to blockB, increments blockB and decrements blockA
        """
        self.blockB += 1
        self.blockA -= 1
        assert self.blockA >= 0
        assert self.blockB >= 0


class Block:
    def __init__(self, name, pmax):
        self.name = name
        self.size = 0
        self.bucket_array = BucketArray(pmax)

    def get_candidate_base_cell(self) -> Cell:
        """
        returns the chosen base cell or None if no such cell was found
        """
        return self.bucket_array.get_candidate_base_cell()

    def add_cell(self, cell: Cell):
        """
        add a cell to this block's bucket list (in the free cell list)
        """
        assert isinstance(cell, Cell)
        self.bucket_array.add_to_free_cell_list(cell)
        self.size += 1

    def move_cell(self, cell: Cell, block):
        """
        move the given cell to the specified block, this should always be its complementary block
        """
        assert isinstance(cell, Cell)
        self.size -= 1
        assert self.size >= 0
        cell.block = block.name
        self.bucket_array.move_cell(cell, 0, block.bucket_array)  # TODO: calc gain
        cell.adjust_net_distribution()


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

    def move_cell(self, cell: Cell, to_gain: int, to_bucket_array):
        """
        move a cell from its bucket to the free cell list of some other bucket array, also adjusting its gain
        """
        assert isinstance(cell, Cell)
        assert isinstance(to_gain, int)
        assert isinstance(to_bucket_array, BucketArray)
        assert cell.locked is False

        assert -self.pmax <= cell.gain <= self.pmax
        assert -self.pmax <= to_gain <= self.pmax
        self[cell.gain].remove(cell)
        if len(self[cell.gain]) == 0:
            self.decrement_max_gain()
        cell.gain = to_gain
        cell.lock()
        to_bucket_array.add_to_free_cell_list(cell)

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
        add a cell to the appropriate bucket, depending on its gain. Adjust max gain index appropriately
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

    def get_candidate_base_cell(self):
        """
        get the first cell of the list that max gain points to. If there is no such cell None is returned
        """
        l = self[self.max_gain]
        if len(l) == 0:
            return None
        else:
            return l[0]
