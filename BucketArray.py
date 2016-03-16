from FiducciaMattheyses import Cell

__author__ = 'gm'


class BucketArray:
    def __init__(self, pmax):
        self.max_gain = 0
        self.pmax = pmax
        self.array = [[]] * (pmax * 2 + 1)
        self.free_cell_list = []

    def __getitem__(self, i: int):
        assert -self.pmax <= i <= self.pmax
        i += self.pmax
        l = self.array[i]
        if len(l) == 0:
            return None
        else:
            return l[i]

    def move_cell(self, cell: Cell, to_gain: int):
        """
        move a cell from its bucket list to the free cell list, also adjusting its gain
        """
        assert isinstance(cell, Cell)
        assert -self.pmax <= cell.gain <= self.pmax
        assert -self.pmax <= to_gain <= self.pmax
        self.array[cell.gain].remove(cell)
        if len(self.array[cell.gain]) == 0:
            self.max_gain -= 1
        cell.gain = to_gain
        self.free_cell_list.append(cell)
