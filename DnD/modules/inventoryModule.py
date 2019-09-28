import tkinter as tk
from typing import Union

import lib.characterLib as char
import lib.components as gui
import lib.helpers as h
import lib.inventoryLib as inv


class ItemDisplay(gui.Section):
    def __init__(self, container: Union[tk.BaseWidget, tk.Tk], item: inv.ItemEntry, **kwargs):
        super().__init__(container, **kwargs)
        self.item = item
        self.name = tk.Label(self.f, text=item.name)
        self.interactions = tk.Frame(self.f)
        self.number = gui.Counter(self.interactions, self.item.quantity, self.set_number)
        # TODO: use needs to display things
        self.use = tk.Button(self.interactions, text='Use', command=self.use)
        self.values = tk.Label(self.f)
        self.description = gui.EffectPane(self.f, h.shorten(self.item.description),
                                          self.item.description)
        self._draw()

    def _draw(self):
        self.name.grid(row=0, column=0)
        self.interactions.grid(row=1, column=0)
        self.number.grid(0, 0)
        self.use.grid(row=0, column=1)
        self.values.grid(row=2, column=0)
        self.description.grid(row=3, column=0)
        self.update_view()

    def update_view(self):
        fmt = 'Total: {:.2f} lb; {:.2f} gp'
        self.values['text'] = fmt.format(self.item.weight * self.item.quantity,
                                         self.item.value * self.item.quantity)
        self.number.set(self.item.quantity)

    def set_number(self, number: int):
        self.item.quantity = number
        self.update_view()

    def use(self):
        description = self.item.use()
        win = tk.Toplevel()
        disp = tk.Label(win, text=description, wraplength=250)
        disp.pack()
        self.update_view()


class InventoryDisplay(gui.Section):
    def __init__(self, container, inventory: inv.OwnedInventory):
        super().__init__(container)
        self.inventory = inventory
        self.owner = inventory.owner
        self.displays = gui.DynamicGrid(self.f)
        for item in inventory:
            self.displays.add(lambda c, i=item: ItemDisplay(c, i))
        self.totals = tk.Label(self.f)
        self._draw()

    def _draw(self):
        self.displays.pack(expand=True, fill=tk.BOTH)
        self.totals.pack()
        self.update_view()

    def update_view(self):
        self.totals['text'] = 'Current load: {}     {}'.format(self.inventory.totalWeight,
                                                               self.inventory.encumbrance)


class Main(gui.MainModule):
    def __init__(self, window: tk.Tk):
        def creator(character: 'char.Character'):
            return InventoryDisplay(window, character.inventory)

        super().__init__(window, creator)


if __name__ == '__main__':
    win = gui.MainWindow()
    Main(win).run()
