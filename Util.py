import copy

__author__ = 'gm'


class Cell:
    def __init__(self, n: int, block):
        assert n >= 0
        self.n = n  # the cell number
        self.pins = 0  # number of nets
        self.nets = set()  # nets that this cell is part of
        self.gain = 0  # the gain of this cell
        self.block = block  # the block this cell belongs to, "A" or "B"
        """:type block Block"""
        self.locked = False  # whether this cell locked or free to move
        self.bucket_num = None  # number of the bucket this cell belongs to
        """:type bucket_num int"""
        self.snapshot = None  # this will hold the state of this cell at the time a snapshot is taken

    def bucket(self):
        if self.block is None:
            return None
        return self.block.bucket_array.array[self.bucket_num]

    def take_snapshot(self):
        """
        take a snapshot of the current state of this cell
        """
        self.snapshot = self.gain, self.block, self.locked, self.bucket_num

    def load_snapshot(self):
        """
        load the saved snapshot of this cell, current cell state will be lost
        """
        assert self.snapshot is not None
        self.gain = self.snapshot[0]
        self.block = self.snapshot[1]
        self.locked = self.snapshot[2]
        self.bucket_num = self.snapshot[3]

    def add_net(self, net):
        if net not in self.nets:
            self.nets.add(net)
            self.pins += 1

    def adjust_net_distribution(self):
        """
        call this after the cell moved to its complementary block, to adjust each net's distribution (each net that
        contains this cell)
        """
        for net in self.nets:
            if self.block.name == "A":  # "A" after move, so the cell moved to "A"
                net.cell_to_blockA(self)
            else:
                assert self.block.name == "B"  # "B" after move, so the cell moved to "B"
                net.cell_to_blockB(self)

    def lock(self):
        if self.locked is True:
            return
        self.locked = True
        for net in self.nets:
            if self.block.name == "A":
                net.blockA_locked += 1
                net.blockA_free -= 1
            else:
                assert self.block.name == "B"
                net.blockB_locked += 1
                net.blockB_free -= 1

    def unlock(self):
        if self.locked is False:
            return
        self.locked = False
        for net in self.nets:
            if self.block.name == "A":
                net.blockA_locked -= 1
                net.blockA_free += 1
            else:
                assert self.block.name == "B"
                net.blockB_locked -= 1
                net.blockB_free += 1

    def yank(self):
        """
        move this cell from its bucket to a new bucket according to its gain. If its gain has not changed then it is
        removed and placed again to the same bucket
        """
        self.block.bucket_array.yank_cell(self)


class Net:
    def __init__(self, n: int):
        assert n >= 0
        self.n = n  # the net number
        self.cells = set()  # the cells that this net contains
        self.blockA_ref = None  # a reference to the block A object
        """:type blockA_ref Block"""
        self.blockB_ref = None  # a reference to the block B object
        """:type blockB_ref Block"""
        self.blockA = 0  # the number of cells in this net that belong to block A
        self.blockB = 0  # the number of cells in this net that belong to block B
        self.blockA_locked = 0  # number of cells in this net that belong to block A and are locked
        self.blockB_locked = 0  # number of cells in this net that belong to block B and are locked
        self.blockA_free = 0  # number of cells in this net that belong to block A and are not locked
        self.blockB_free = 0  # number of cells in this net that belong to block B and are not locked
        self.blockA_cells = []  # the cells that belong to this net and are part of block A
        self.blockB_cells = []  # the cells that belong to this net and are part of block B
        self.cut = False  # whether this net is cut. This means that it has cells both in block A and B
        self.snapshot = None  # this will hold the state of this net at the time a snapshot is taken

    def take_snapshot(self):
        """
        take a snapshot of the current state of this net
        """
        self.snapshot = self.blockA, self.blockB, self.blockA_locked, self.blockB_locked, self.blockA_free, \
                        self.blockB_free, copy.copy(self.blockA_cells), copy.copy(self.blockB_cells), self.cut

    def load_snapshot(self):
        """
        load the saved snapshot of this net, current net state will be lost
        """
        assert self.snapshot is not None
        self.blockA = self.snapshot[0]
        self.blockB = self.snapshot[1]
        self.blockA_locked = self.snapshot[2]
        self.blockB_locked = self.snapshot[3]
        self.blockA_free = self.snapshot[4]
        self.blockB_free = self.snapshot[5]
        self.blockA_cells = self.snapshot[6]
        self.blockB_cells = self.snapshot[7]
        self.cut = self.snapshot[8]

    def add_cell(self, cell):
        """
        add a cell to this net, increment blockA or blockB numbers depending on what block the added cell belongs to
        """
        if cell not in self.cells:
            self.cells.add(cell)
            if cell.block == "A":
                self.blockA += 1
                self.blockA_free += 1
                self.blockA_cells.append(cell)
            else:
                assert cell.block == "B"
                self.blockB += 1
                self.blockB_free += 1
                self.blockB_cells.append(cell)

    def __update_cut_state(self):
        new_cutstate = self.blockA != 0 and self.blockB != 0
        if self.cut != new_cutstate:
            if new_cutstate is True:
                self.blockA_ref.fm.cutset += 1
            else:
                self.blockA_ref.fm.cutset -= 1
            self.cut = new_cutstate

    def cell_to_blockA(self, cell):
        """
        call this when a cell moved to blockA, increments blockA and decrements blockB
        """
        self.blockA += 1
        self.blockB -= 1
        if cell.locked is True:
            self.blockA_locked += 1
            self.blockB_locked -= 1
        else:
            self.blockA_free += 1
            self.blockB_free -= 1

        self.blockB_cells.remove(cell)
        self.blockA_cells.append(cell)
        self.__update_cut_state()
        assert self.blockA >= 0
        assert self.blockA_free >= 0
        assert self.blockB >= 0
        assert self.blockB_free >= 0
        assert self.blockA_free + self.blockA_locked == self.blockA
        assert self.blockB_free + self.blockB_locked == self.blockB

    def cell_to_blockB(self, cell):
        """
        call this when a cell moved to blockB, increments blockB and decrements blockA
        """
        self.blockB += 1
        self.blockA -= 1
        if cell.locked is True:
            self.blockB_locked += 1
            self.blockA_locked -= 1
        else:
            self.blockB_free += 1
            self.blockA_free -= 1
        self.blockA_cells.remove(cell)
        self.blockB_cells.append(cell)
        self.__update_cut_state()
        assert self.blockA >= 0
        assert self.blockA_free >= 0
        assert self.blockB >= 0
        assert self.blockB_free >= 0
        assert self.blockA_free + self.blockA_locked == self.blockA
        assert self.blockB_free + self.blockB_locked == self.blockB

    def inc_gains_of_free_cells(self):
        """
        increments gains of all free cells in this net that are not locked. This should be called before the move
        """
        for cell in self.cells:
            if not cell.locked:
                cell.gain += 1
                cell.yank()

    def dec_gain_Tcell(self, to_side: str):
        """
        decrements the gain of the only T cell in this net if it is free. This should be called before the move
        """
        assert self.blockA_ref is not None
        assert self.blockB_ref is not None

        if to_side == "A":
            assert self.blockA_free == 1
            assert len(self.blockA_cells) == 1
            cell = self.blockA_cells[0]
            cell.gain -= 1
            cell.yank()
        else:
            assert to_side == "B"
            assert self.blockB_free == 1
            assert len(self.blockB_cells) == 1
            cell = self.blockB_cells[0]
            cell.gain -= 1
            cell.yank()

    def dec_gains_of_free_cells(self):
        """
        decrements gains of all free cells in this net that are not locked. This should be called after the move
        """
        for cell in self.cells:
            if not cell.locked:
                cell.gain -= 1
                cell.yank()

    def inc_gain_Fcell(self, from_side: str):
        """
        increments the gain of the only F cell in this net if it is free. This should be called after the move
        """
        assert self.blockA_ref is not None
        assert self.blockB_ref is not None

        if from_side == "A":
            assert self.blockA_free == 1
            assert len(self.blockA_cells) == 1
            cell = self.blockA_ref.cells[0]
            cell.gain += 1
            cell.yank()
        else:
            assert from_side == "B"
            assert self.blockB_free == 1
            assert len(self.blockB_cells) == 1
            cell = self.blockB_ref.cells[0]
            cell.gain += 1
            cell.yank()


class Block:
    def __init__(self, name: str, pmax: int, fm):
        self.name = name
        self.size = 0
        self.bucket_array = BucketArray(pmax)
        self.cells = []  # cells that belong to this block
        self.fm = fm  # top level object FiducciaMattheyses that contains this block
        """:type fm FiducciaMattheyses.FiducciaMattheyses"""
        self.snapshot = None  # this will hold the state of this block at the time a snapshot is taken

    def take_snapshot(self):
        """
        take a snapshot of the current state of this block
        """
        self.snapshot = self.name, self.size, copy.copy(self.cells)
        self.bucket_array.take_snapshot()

    def load_snapshot(self):
        """
        load the saved snapshot of this block, current block state will be lost
        """
        assert self.snapshot is not None
        self.name = self.snapshot[0]
        self.size = self.snapshot[1]
        self.cells = self.snapshot[2]
        self.bucket_array.load_snapshot()

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
        self.cells.append(cell)
        cell.block = self
        self.size += 1

    def remove_cell(self, cell: Cell):
        """
        remove a cell from this block's bucket list
        """
        assert isinstance(cell, Cell)
        self.size -= 1
        assert self.size >= 0
        self.cells.remove(cell)
        self.bucket_array.remove_cell(cell)

    def move_cell(self, cell: Cell):
        """
        move the given cell to its complementary block
        """
        assert isinstance(cell, Cell)
        comp_block = cell.block.fm.blockA if cell.block.name == "B" else cell.block.fm.blockB
        # lock cell
        cell.lock()
        # Adjust gains and yank cells before the move
        self.__adjust_gains_before_move(cell)
        # Remove cell from this block
        self.remove_cell(cell)
        # Add cell to complementary block
        comp_block.add_cell(cell)
        # Adjust the distribution of this cell's nets to reflect the move
        cell.adjust_net_distribution()
        # Adjust gains and yank cells after the move
        self.__adjust_gains_after_move(cell)

    def __adjust_gains_before_move(self, cell: Cell):
        assert isinstance(cell, Cell)
        for net in cell.nets:
            if cell.block.name == "A":
                LT = net.blockB_locked
                FT = net.blockB_free
            else:
                assert cell.block.name == "B"
                LT = net.blockA_locked
                FT = net.blockA_free
            if LT == 0:
                if FT == 0:
                    net.inc_gains_of_free_cells()
                elif FT == 1:
                    net.dec_gain_Tcell("A" if cell.block.name == "B" else "B")

    def __adjust_gains_after_move(self, cell: Cell):
        assert isinstance(cell, Cell)
        for net in cell.nets:
            if cell.block.name == "A":
                LF = net.blockB_locked
                FF = net.blockB_free
            else:
                assert cell.block.name == "B"
                LF = net.blockA_locked
                FF = net.blockA_free
            if LF == 0:
                if FF == 0:
                    net.dec_gains_of_free_cells()
                elif FF == 1:
                    net.inc_gain_Fcell("A" if cell.block.name == "B" else "B")

    def initialize(self):
        """
        move cells from the free cell list of this block's bucket list back to the appropriate buckets
        """
        self.bucket_array.initialize()


class BucketArray:
    def __init__(self, pmax):
        self.max_gain = -pmax
        self.pmax = pmax
        self.array = [[] for x in range(pmax * 2 + 1)]
        self.free_cell_list = []
        self.snapshot = None  # this will hold the state of this bucket array at the time a snapshot is taken

    def take_snapshot(self):
        """
        take a snapshot of the current state of this bucket array
        """
        self.snapshot = self.max_gain, self.__dup_array(), copy.copy(self.free_cell_list)

    def __dup_array(self):
        clone = []
        for i in self.array:
            clone.append(copy.copy(i))
        return clone

    def load_snapshot(self):
        """
        load the saved snapshot of this bucket array, current bucket array state will be lost
        """
        assert self.snapshot is not None
        self.max_gain = self.snapshot[0]
        self.array = self.snapshot[1]
        self.free_cell_list = self.snapshot[2]

    def __getitem__(self, i: int) -> list:
        assert -self.pmax <= i <= self.pmax
        i += self.pmax
        return self.array[i]

    def remove_cell(self, cell: Cell):
        """
        remove specified cell from this bucket list
        """
        assert isinstance(cell, Cell)
        cell.bucket().remove(cell)
        if self[self.max_gain] == cell.bucket() and len(cell.bucket()) == 0:
            self.decrement_max_gain()
        cell.bucket_num = None

    def yank_cell(self, cell: Cell):
        """
        move a cell from its bucket to a new bucket according to its gain. If its gain has not changed then it is
        removed and placed again to the same bucket
        """
        assert isinstance(cell, Cell)
        assert cell.locked is False

        assert -self.pmax <= cell.gain <= self.pmax
        self.remove_cell(cell)
        self.add_cell(cell)

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
        cell.bucket_num = cell.gain + self.pmax
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

    def initialize(self):
        """
        move cells from the free cell list back to the appropriate buckets
        """
        for cell in self.free_cell_list:
            cell.unlock()
            self.add_cell(cell)
        self.free_cell_list.clear()
