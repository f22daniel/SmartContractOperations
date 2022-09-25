from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton


class ConstructorLabel(Label):
    pass


class ClickInput(TextInput):

    def on_focus(self, instance, value):
        if value:
            print(f'Value: {value}')
            self.text = ''

    def on_size(self, instance, value):
        self.font_size = 14
        self.multiline = False


class ConstructorText(ClickInput):

    def on_size(self, instance, value):
        self.size_hint = (None, 1)
        self.width = 150


class ContractInput(ClickInput):
    pass


class SubContractButton(ToggleButton):
    pass


class ViewButton(Button):
    pass


class NonepayableButton(Button):
    pass


class PayableButton(Button):
    pass


class StandardToggle(ToggleButtonBehavior, Button):

    def on_state(self, widget, value):
        if value == 'down':
            self.col = (0/255, 77/255, 0, 1)
        else:
            self.col = (128/255, 77/255, 0, 1)


class OutputLabel(Label):
    pass


class InputLabel(Label):
    pass


class Input(TextInput):
    pass

class CompilerButton(ToggleButton):
    pass

class GanacheAddressIndex(Label):
    pass

class GanacheAddress(Label):
    pass