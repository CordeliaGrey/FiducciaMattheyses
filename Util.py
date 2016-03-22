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
        self.bucket = None  # reference to the bucket this cell belongs to
        """:type bucket list"""

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
        self.blockA_free = 0    # number of cells in this net that belong to block A and are not locked
        self.blockB_free = 0    # number of cells in this net that belong to block B and are not locked
        self.blockA_cells = []  # the cells that belong to this net and are part of block A
        self.blockB_cells = []  # the cells that belong to this net and are part of block B
        self.cut = False        # whether this net is cut. This means that it has cells both in block A and B

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

    def cell_to_blockA(self, cell):
        """
        call this when a cell moved to blockA, increments blockA and decrements blockB
        """
        self.blockA += 1
        self.blockA_free += 1
        self.blockB -= 1
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
        self.blockB_free += 1
        self.blockA -= 1
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

    def dec_gain_Tcell(self, to_side: str):
        """
        decrements the gain of the only T cell in this net if it is free. This should be called before the move
        """
        assert self.blockA_ref is not None
        assert self.blockB_ref is not None

        if to_side == "A":
            assert self.blockA_free == 1
            assert len(self.blockA_cells) == 1
            self.blockA_cells[0].gain -= 1
        else:
            assert to_side == "B"
            assert self.blockB_free == 1
            assert len(self.blockB_cells) == 1
            self.blockB_cells[0].gain -= 1

    def dec_gains_of_free_cells(self):
        """
        decrements gains of all free cells in this net that are not locked. This should be called after the move
        """
        for cell in self.cells:
            if not cell.locked:
                cell.gain -= 1

    def inc_gain_Fcell(self, from_side: str):
        """
        increments the gain of the only F cell in this net if it is free. This should be called after the move
        """
        assert self.blockA_ref is not None
        assert self.blockB_ref is not None

        if from_side == "A":
            assert self.blockA_free == 1
            assert len(self.blockA_ref.cells) == 1
            self.blockA_ref.cells[0].gain += 1
        else:
            assert from_side == "B"
            assert self.blockB_free == 1
            assert len(self.blockB_ref.cells) == 1
            self.blockB_ref.cells[0].gain += 1


class Block:
    def __init__(self, name, pmax, fm):
        self.name = name
        self.size = 0
        self.bucket_array = BucketArray(pmax)
        self.cells = []  # cells that belong to this block
        self.fm = fm  # top level object FiducciaMattheyses that contains this block

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
        self.size += 1

    def move_cell(self, cell: Cell, block):
        """
        move the given cell to the specified block, this should always be its complementary block
        """
        assert isinstance(cell, Cell)
        old_gain = cell.gain
        self.__adjust_gains_before_move(cell)
        self.size -= 1
        self.cells.remove(cell)
        block.cells.append(cell)
        assert self.size >= 0
        cell.block = block
        self.bucket_array.move_cell(cell, old_gain, block.bucket_array)
        self.__adjust_gains_after_move(cell)

        block.size += 1
        cell.adjust_net_distribution()

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
                LF = net.blockA_locked
                FF = net.blockA_free
            else:
                assert cell.block.name == "B"
                LF = net.blockB_locked
                FF = net.blockB_free
            if LF == 0:
                if FF == 0:
                    net.dec_gains_of_free_cells()
                elif FF == 1:
                    net.inc_gain_Fcell("A" if cell.block == "B" else "B")

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

    def __getitem__(self, i: int) -> list:
        assert -self.pmax <= i <= self.pmax
        i += self.pmax
        return self.array[i]

    def move_cell_to_complementary_block(self):
        """
        move specified cell to its complementary block (in its free cell list) and lock it
        """
        pass
        # TODO implement

    def move_cell(self, cell: Cell, old_gain: int, to_bucket_array):
        """
        move a cell from its bucket to the free cell list of some other bucket array. The cell's gain is already
        updated at this point by the "before move" adjustments. Old_gain is the cell's gain before that
        adjustment and thus also reflects the index this cell resides in the bucket array
        """
        assert isinstance(cell, Cell)
        assert isinstance(old_gain, int)
        assert isinstance(to_bucket_array, BucketArray)
        assert cell.locked is False

        assert -self.pmax <= cell.gain <= self.pmax
        assert -self.pmax <= old_gain <= self.pmax
        self[old_gain].remove(cell)
        if len(self[old_gain]) == 0:
            self.decrement_max_gain()
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
        cell.bucket = self[cell.gain]
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
