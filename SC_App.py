import ast
import binascii
# import json
import webbrowser

from functools import partial
import requests.exceptions
import solcx.exceptions
import web3
from etherscan import Etherscan
from kivy.app import App
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import *
from plyer import filechooser
from solcx import compile_standard, install_solc
from web3 import Web3
from web3 import exceptions
from SC_Constants import compiler_list, full_compiler_list
from SC_Widgets import *
from SC_Variables import *

# SC variables
w3 = ''

Builder.load_file('SC_App.kv')
Window.size = (1100, 600)


class PrivateKeyPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class PrivateKeyPopup2(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class GanachePopup(Popup):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        global w3
        if settings_test.network != 'ganache':
            settings_test.network = 'ganache'
        try:
            w3 = Web3(Web3.HTTPProvider(settings_test.ganache_rpc))
            addresses = w3.eth.accounts
            for x in range(len(addresses)):
                balance = w3.eth.get_balance(f"{addresses[x]}")
                balance = Web3.fromWei(int(balance), 'ether')
                balance = round(balance, 2)
                ganache_address_index = GanacheAddressIndex(text=f'Address {x + 1}: ')
                ganache_address_widget = CompilerButton(text=f'{addresses[x]}')
                ganache_address_balance = GanacheAddressIndex(text=f'{balance} ETH')
                self.ids[f'{addresses[x]}'] = ganache_address_widget
                self.ids.ganache_address_list.add_widget(ganache_address_index)
                self.ids.ganache_address_list.add_widget(ganache_address_widget)
                self.ids.ganache_address_list.add_widget(ganache_address_balance)
                ganache_address_widget.bind(on_release=partial(self.ganache_address_selection, ganache_address_widget.text, ganache_address_balance.text))
                self.ids.ganache_status.text = 'Ganache Established'
        except requests.exceptions.ConnectionError as e:
            e = str(e)
            self.ids.ganache_status.text = e[:47]

    @staticmethod
    def ganache_address_selection(text, amount, state):
        print(f'Button pressed: {text}')
        print(f'amount: {amount}')
        settings_test.ganache_address = text
        SmartContractOperationsApp.mylayout.address_cutting()
        SmartContractOperationsApp.mylayout.ganache_address_balance(amount)


class NetworkPopup(Popup):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        c_network = settings_test.network.capitalize()
        self.ids[f'{c_network}'].state = 'down'


class CompilerPopup(Popup):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        compiler = settings_test.solidity_compiler
        compiler = f'v{compiler}'
        compiler = compiler.replace('.', '_')
        print(f'Compiler: {compiler}')
        self.ids[f'{compiler}'].state = 'down'


class AddressPopup(Popup):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        bool = None
        self.ids.address_popup.text = settings_test.address
        self.ids.private_key_popup.text = settings_test.private_key
        for x in range(1, 7):
            if settings_test.address == settings_test.addresses[f'Address {x}']:
                print(f'settings addresses: {settings_test.addresses[f"Address {x}"]}')
                self.ids[f'Address{x}'].state = 'down'
        for x in range(1, 7):
            if self.ids[f'Address{x}'].state == 'down':
                bool = False
                break
            else:
                bool = True
        if bool is True:
            self.ids[f'Address1'].state = 'down'

    def select_address(self, address):

        if address == 'Address 1':
            self.ids.address_popup.text = settings_test.address_1
            self.ids.private_key_popup.text = settings_test.private_key_1
        elif address == 'Address 2':
            self.ids.address_popup.text = settings_test.address_2
            self.ids.private_key_popup.text = settings_test.private_key_2
        elif address == 'Address 3':
            self.ids.address_popup.text = settings_test.address_3
            self.ids.private_key_popup.text = settings_test.private_key_3
        elif address == 'Address 4':
            self.ids.address_popup.text = settings_test.address_4
            self.ids.private_key_popup.text = settings_test.private_key_4
        elif address == 'Address 5':
            self.ids.address_popup.text = settings_test.address_5
            self.ids.private_key_popup.text = settings_test.private_key_5
        else:
            self.ids.address_popup.text = settings_test.address_6
            self.ids.private_key_popup.text = settings_test.private_key_6
        settings_test.address = self.ids.address_popup.text
        settings_test.private_key = self.ids.private_key_popup.text
        Settings.update_json(settings_test)

    def address_enter_popup(self, state, input):
        print(f'Address entered {state} and {input}')
        input = input.strip()
        if state is False:
            print(f'Address validation: {Web3.isAddress(input)}')
            self.ids.address_popup.text = input
            settings_test.address = input
            if self.ids['Address1'].state == 'down':
                settings_test.address_1 = input
            elif self.ids['Address2'].state == 'down':
                settings_test.address_2 = input
            elif self.ids['Address3'].state == 'down':
                settings_test.address_3 = input
            elif self.ids['Address4'].state == 'down':
                settings_test.address_4 = input
            elif self.ids['Address5'].state == 'down':
                settings_test.address_5 = input
            else:
                settings_test.address_6 = input
            Settings.update_json(settings_test)

    def private_key_enter_popup(self, state, input):
        input = input.strip()
        if f'{input}'[:2] != '0x':
            input = f'0x{input}'
        if state is False:
            self.ids.private_key_popup.text = input
            settings_test.private_key = input
            if self.ids['Address1'].state == 'down':
                settings_test.private_key_1 = input
            elif self.ids['Address2'].state == 'down':
                settings_test.private_key_2 = input
            elif self.ids['Address3'].state == 'down':
                settings_test.private_key_3 = input
            elif self.ids['Address4'].state == 'down':
                settings_test.private_key_4 = input
            elif self.ids['Address5'].state == 'down':
                settings_test.private_key_5 = input
            else:
                settings_test.private_key_6 = input
            Settings.update_json(settings_test)


class SettingsPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.ids.APIEnter.text = settings_test.etherscan_api
        self.ids.BSCAPIEnter.text = settings_test.bsc_api
        self.ids.InfuraEnter.text = settings_test.infura_api
        self.ids.GanacheRPCEnter.text = settings_test.ganache_rpc
        self.ids.GanacheIDEnter.text = str(settings_test.ganache_id)

    @staticmethod
    def api_enter_popup(state, input):

        if state is False:
            input = input.strip()
            print(f'input: {input}')
            settings_test.etherscan_api = input
            if settings_test.network != 'ganache':
                variables_test.ethsc = Etherscan(settings_test.etherscan_api, net=settings_test.network)
            else:
                pass
            Settings.update_json(settings_test)

    @staticmethod
    def infura_enter_popup(state, input):
        global w3
        if state is False:
            input = input.strip()
            settings_test.infura_api = input
            settings_test.infura_link = f'https://{settings_test.network}.infura.io/v3/{input}'
            w3 = Web3.HTTPProvider(settings_test.infura_link)
            Settings.update_json(settings_test)

    @staticmethod
    def ganache_rpc_enter_popup(state, input):

        if state is False:
            input = input.strip()
            settings_test.ganache_rpc = int(input)
            Settings.update_json(settings_test)

    @staticmethod
    def ganache_id_enter_popup(state, input):

        if state is False:
            input = input.strip()
            settings_test.ganache_id = int(input)
            Settings.update_json(settings_test)

    @staticmethod
    def bsc_api_enter_popup(state, input):

        if state is False:
            input = input.strip()
            settings_test.bsc_api = input
            Settings.update_json(settings_test)


class MyLayout(TabbedPanel):

    def __init__(self, **kwargs):
        global w3
        super().__init__(**kwargs)
        try:
            self.update_prices()
            # Set up w3 protocol
            if settings_test.network != 'ganache':
                self.ids.active_network.text = f'{settings_test.network.title()}'
                self.ids.network_active_sc.text = f'{settings_test.network.title()}'
                w3 = Web3(Web3.HTTPProvider(f'{settings_test.infura_link}'))
            elif settings_test.network == 'binance':
                self.ids.active_network.text = 'BSC'
                self.ids.network_active_sc.text = 'BSC'
            else:
                self.ids.active_network.text = 'Ganache'
                self.ids.network_active_sc.text = 'Ganache'
                w3 = Web3(Web3.HTTPProvider(settings_test.ganache_rpc))
            # Compiler setup
            self.ids.compiler_set.text = settings_test.full_compiler
            # Currency selection
            self.ids.currency_selection.text = 'Wei'
            # Total gas spent
            print(settings_test.total_gas_used)
            self.ids.total_gas_used_sc.text = settings_test.total_gas_used
            self.ids.total_gwei_spent_sc.text = settings_test.total_gwei_spent
            self.ids.total_usd_spent_sc.text = settings_test.total_usd_spent
            self.ids.total_gwei_spent.text = settings_test.total_gwei_spent
            self.ids.total_usd_spent.text = settings_test.total_usd_spent
            # Last gas spent
            self.ids.last_gas_spent.text = '0'
            self.ids.last_gwei_spent.text = '0'
            self.ids.last_usd_spent.text = '0'
            self.ids.last_gas_spent_sc.text = '0'
            self.ids.last_gwei_spent_sc.text = '0'
            self.ids.last_usd_spent_sc.text = '0'
            self.address_cutting()
        except AssertionError as e:
            self.ids.StatusBar.text = str(e)
        except ValueError as e:
            self.ids.StatusBar.text = str(e)
        except requests.exceptions.ConnectionError as e:
            self.ids.StatusBar.text = str(e)

    def address_enter(self, state):

        if state is False:
            self.address_cutting()
            print('Saved')

    # ################################################-Tab 2-################################################

    # Active address selection
    def address_selection(self):

        try:
            self.address_cutting()
            self.update_prices()
        except web3.exceptions.InvalidAddress:
            self.ids.AddressEnter.text = ''
            self.ids.PrivateKeyEnter.text = ''
            self.ids.Wallet_Balance.text = ''
            self.ids.wallet_balance_sc.text = ''
            self.ids.address_active.text = ''
            self.ids.address_active_sc.text = ''

    # Network selection
    def network_selection(self, selection, chainid):
        global w3
        try:
            settings_test.network = str.lower(selection)

            if settings_test.network == 'ganache':
                settings_test.network = 'ganache'
                w3 = Web3(Web3.HTTPProvider(settings_test.ganache_rpc))
                self.ids.active_network.text = selection.title()
                self.ids.network_active_sc.text = selection.title()
                self.address_cutting()
            elif settings_test.network == 'binance smart chain':
                print('BSC selected')
                settings_test.network = 'binance'
                self.ids.active_network.text = 'BSC'
                self.ids.network_active_sc.text = 'BSC'
            else:
                if settings_test.network == 'mainnet':
                    variables_test.ethsc = Etherscan(settings_test.etherscan_api, net='main')
                    settings_test.contract_web_page = f'https://etherscan.io/address/'
                else:
                    variables_test.ethsc = Etherscan(settings_test.etherscan_api, net=settings_test.network)
                    settings_test.contract_web_page = f'https://{settings_test.network}.etherscan.io/address/'
                    print(f'Type: {variables_test.ethsc}')
                settings_test.infura_link = f'https://{settings_test.network}.infura.io/v3/{settings_test.infura_api}'

                w3 = Web3(Web3.HTTPProvider(settings_test.infura_link))
                settings_test.chain_id = chainid
                variables_test.balance = w3.eth.getBalance(f'{settings_test.address}')
                variables_test.balance = float(variables_test.balance) / 10 ** 18
                variables_test.balance = round(variables_test.balance, 5)
                print(f'Balance: {variables_test.balance}')
                self.ids.Wallet_Balance.text = str(f'{variables_test.balance} ETH')
                self.ids.wallet_balance_sc.text = str(f'{variables_test.balance} ETH')
                self.ids.active_network.text = selection.title()
                self.ids.network_active_sc.text = selection.title()
                self.address_cutting()

            Settings.update_json(settings_test)
        except AssertionError as e:
            self.ids.StatusBar.text = str(e)
            self.ids.ETH_Price.text = 'N/A'
            self.ids.eth_price_sc.text = 'N/A'
            self.ids.Gas_Price.text = 'N/A'
            self.ids.Gas_Price_USD.text = 'N/A'
            self.ids.Conf_Time.text = 'N/A'
        except requests.exceptions.ConnectionError:
            pass

    def update_prices(self):
        global w3
        try:

            # w3 declaration
            if settings_test.network != 'ganache':
                w3 = Web3(Web3.HTTPProvider(settings_test.infura_link))
            else:
                w3 = Web3(Web3.HTTPProvider(settings_test.ganache_rpc))

            # ETH Price update

            variables_test.ethsc = Etherscan(settings_test.etherscan_api, net='main')
            # variables_test.price = variables_test.ethsc.get_eth_last_price()
            # variables_test.eth_price = variables_test.price['ethusd']
            variables_test.eth_price = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd').json()
            variables_test.eth_price = variables_test.eth_price['ethereum']['usd']
            variables_test.eth_price = round(float(variables_test.eth_price), 0)
            self.ids.ETH_Price.text = f'{int(variables_test.eth_price)} USD'
            self.ids.eth_price_sc.text = f'{int(variables_test.eth_price)} USD'
            print(self.ids.ETH_Price.text)
            # Gas Price update
            gas = variables_test.ethsc.get_gas_oracle()
            variables_test.gas_price = gas['SafeGasPrice']
            self.ids.Gas_Price.text = f'{variables_test.gas_price} Gwei'
            print(self.ids.Gas_Price.text)
            # Gas Price USD update
            variables_test.gas_price_usd = float(variables_test.gas_price) * 0.000000001 * float(variables_test.eth_price)
            self.ids.Gas_Price_USD.text = f"{str('{:f}'.format(variables_test.gas_price_usd))} USD"
            print(self.ids.Gas_Price_USD.text)
            # Confirmation time update
            variables_test.gas_price_wei = int(variables_test.gas_price) * 1000000000
            variables_test.conf_time = variables_test.ethsc.get_est_confirmation_time(variables_test.gas_price_wei)
            self.ids.Conf_Time.text = f'{variables_test.conf_time} s'
            print(self.ids.Conf_Time.text)
            # Wallet Balance update
            if settings_test.network == 'ganache':
                w3_balance = w3.eth.getBalance(settings_test.ganache_address)
                w3_balance = float(w3_balance) / 10 ** 18
                w3_balance = round(w3_balance, 5)
                self.ids.Wallet_Balance.text = str(f'{w3_balance} ETH')
                self.ids.wallet_balance_sc.text = str(f'{w3_balance} ETH')
            else:
                variables_test.balance = w3.eth.getBalance(f'{settings_test.address}')
                variables_test.balance = float(variables_test.balance) / 10 ** 18
                variables_test.balance = round(variables_test.balance, 5)
                self.ids.Wallet_Balance.text = str(f'{variables_test.balance} ETH')
                self.ids.wallet_balance_sc.text = str(f'{variables_test.balance} ETH')
                print(self.ids.Wallet_Balance.text)
            self.ids.StatusBar.text = 'Ready to work'
        except AssertionError as e:
            self.ids.StatusBar.text = str(e)
            self.ids.ETH_Price.text = 'N/A'
            self.ids.Gas_Price.text = 'N/A'
            self.ids.Gas_Price_USD.text = 'N/A'
            self.ids.Conf_Time.text = 'N/A'
        except web3.exceptions.InvalidAddress as e:
            self.ids.StatusBar.text = str(e)
            self.ids.Wallet_Balance.text = 'N/A'
            self.ids.wallet_balance_sc.text = 'N/A'

    # SC file selection
    def file_chooser(self):
        filechooser.open_file(on_selection=self.selected)
        self.ids.compile_sc.disabled = False
        self.ids.ChooseSC.disabled = True

    def selected(self, selection):
        try:
            print(selection[0])
            variables_test.sc_file_path = selection[0]
            self.ids.FilePath.text = variables_test.sc_file_path
        except IndexError:
            pass

    def clear(self):
        self.ids.Constructor.clear_widgets()
        self.ids.FilePath.text = ''
        variables_test.sc_file_path = ''
        variables_test.sc_file_name = ''
        variables_test.sc_file_keys = []
        variables_test.compiled_contract = ''
        variables_test.constructor_inputs = []

        # Label clearing
        self.ids.GasEstimate.text = ''
        self.ids.GasCost.text = ''
        self.ids.GasCostUSD.text = ''
        self.ids.UploadCost.text = ''
        self.ids.UploadCostUSD.text = ''
        self.ids.ContractSelection.clear_widgets()
        self.ids.StatusBar.text = 'Select SC file'
        # Buttons enabling/disabling
        self.ids.DeploySC.disabled = True
        self.ids.Calculate.disabled = True
        self.ids.ChooseSC.disabled = False
        self.ids.copy_contract_address.disabled = True

    def compile(self):
        global compiler_list, full_compiler_list

        variables_test.sc_file_name = ''
        subcontract_name = []
        # Open SC file
        try:
            with open(f'{variables_test.sc_file_path}', "r") as file:
                sc_file = file.read()

            for i in reversed(variables_test.sc_file_path):
                if i == '/':
                    break
                variables_test.sc_file_name = i + variables_test.sc_file_name

            # Compiler selector
            for x in range(len(compiler_list)):
                if f'{compiler_list[x]}' in sc_file:
                    settings_test.solidity_compiler = f'{compiler_list[x]}'
                    settings_test.full_compiler = f'{full_compiler_list[x]}'
                    install_solc(f'{settings_test.solidity_compiler}')
                    self.ids.compiler_set.text = settings_test.full_compiler
                    break
            Settings.update_json(settings_test)
            # Compile SC
            variables_test.compiled_contract = compile_standard(
                {
                    'language': 'Solidity',
                    'sources': {f'{variables_test.sc_file_name}': {'content': sc_file}},
                    'settings': {
                        'outputSelection': {
                            '*': {'*': ['abi', 'metadata', 'evm.bytecode', 'evm.sourceMap']}
                        }
                    },
                }, solc_version=settings_test.solidity_compiler)

            with open('compiled_code.json', 'w') as file:
                json.dump(variables_test.compiled_contract, file, indent=1)

            # Get SC_file_keys
            def get_all_keys(def_compiled_contract):
                for key, value in def_compiled_contract.items():
                    yield key
                    if isinstance(value, dict):
                        yield from get_all_keys(value)

            for j in get_all_keys(variables_test.compiled_contract):
                variables_test.sc_file_keys.append(j)
            print(f'sc_file_keys: {variables_test.sc_file_keys}')
            # Get Subcontracts
            for iterator, _ in enumerate(variables_test.sc_file_keys):
                if variables_test.sc_file_keys[iterator] == 'abi':
                    subcontract_name.append(variables_test.sc_file_keys[iterator - 1])
                    print(f'subcontracts: {subcontract_name}')

            # Enable/Disable buttons
            self.ids.compile_sc.disabled = True
            self.ids.select_sc.disabled = False
            # Create JSON file
            Settings.update_json(settings_test)
            # Create Buttons
            for iterator, _ in enumerate(subcontract_name):
                # Parametrise buttons
                new_toggle = SubContractButton(text=subcontract_name[iterator])
                # Add ID to buttons
                self.ids[subcontract_name[iterator]] = new_toggle
                new_toggle.bind(on_release=partial(self.select_subcontract, new_toggle.text))
                print(f'ToggleID: {self.ids[subcontract_name[iterator]]}')
                print(self.ids[subcontract_name[iterator]].state)
                # Create buttons
                self.ids.ContractSelection.add_widget(new_toggle)

            self.ids.select_sc.disabled = False
            self.ids.StatusBar.text = 'Select Subcontract!'
        except solcx.exceptions.SolcNotInstalled as e:
            print(e)
            self.ids.StatusBar.text = 'Wrong Solidity compiler selected'
        except FileNotFoundError:
            self.ids.FilePath.text = 'File not found'
        except solcx.exceptions.SolcError as e:
            self.ids.StatusBar.text = 'Wrong compiler or incorrect syntax in Solidity file. Please check Settings or Contract'
            print(e)
            # solc_error = str(e)
            # print(f'{solc_error}')
        except AttributeError:
            pass

    def select_subcontract(self, text, *args):

        constructor = []
        constructor_id = 0
        try:
            variables_test.subcontract = text
            print(f'subcontract: {variables_test.subcontract}')
            with open('compiled_code.json', 'r') as file:
                variables_test.compiled_contract = json.loads(file.read())
            print('Checkpoint 1')
            # Get Bytecode
            variables_test.bytecode = \
            variables_test.compiled_contract['contracts'][f'{variables_test.sc_file_name}'][f'{variables_test.subcontract}']['evm']['bytecode'][
                'object']
            print(f'bytecode: {variables_test.bytecode}')
            # Get ABI
            variables_test.abi = variables_test.compiled_contract['contracts'][f'{variables_test.sc_file_name}'][f'{variables_test.subcontract}']['abi']
            print(f'abi: {variables_test.abi}')
            # Get Contructor
            for z in variables_test.abi:
                i = ''
                for i in z.values():
                    pass
                if i == 'constructor':
                    constructor = z
                    break
            print(f'constructor: {constructor}')
            # Create Constructor Icons
            if len(constructor) != 0:
                for x in constructor.get('inputs'):
                    # Parametrize widgets
                    new_label = ConstructorLabel(text=x.get('name'), markup=True, bold=True, font_size=18)
                    new_text = ConstructorText(text=x.get('type'), font_size=16)
                    # Add ID to text inputs
                    self.ids[f'ConstructorInput_{constructor_id}'] = new_text
                    print(self.ids[f'ConstructorInput_{constructor_id}'].text)
                    variables_test.constructor_inputs.append(self.ids[f'ConstructorInput_{constructor_id}'].text)
                    constructor_id += 1

                    # Create widgets
                    self.ids.Constructor.add_widget(new_label)
                    self.ids.Constructor.add_widget(new_text)
                    self.ids.StatusBar.text = 'Insert constructor data!'
            if constructor_id == 0:
                self.ids.StatusBar.text = 'Calculate Upload Cost!'

            # Buttons enabling/disabling
            self.ids.compile_sc.disabled = True
            self.ids.Calculate.disabled = False
            self.ids.ChooseSC.disabled = True
        except KeyError as e:
            self.ids.StatusBar.text = 'Subcontract not selected!'
            print(f'Error: {e}')

    def calculate_upload(self):
        global w3

        try:
            constructor_count = 0
            ''''''
            # w3 declaration
            if settings_test.network != 'ganache':
                w3 = Web3(Web3.HTTPProvider(settings_test.infura_link))
            else:
                w3 = Web3(Web3.HTTPProvider(settings_test.ganache_rpc))
            print(f'abi: {variables_test.abi}')
            print(f'bytecode: {variables_test.bytecode}')

            for _ in variables_test.constructor_inputs:
                if 'uint' in variables_test.constructor_inputs[constructor_count]:
                    variables_test.constructor_inputs[constructor_count] = int(self.ids[f'ConstructorInput_{constructor_count}'].text)
                    constructor_count += 1
                    print('uint')
                elif 'string' in variables_test.constructor_inputs[constructor_count]:
                    variables_test.constructor_inputs[constructor_count] = str(self.ids[f'ConstructorInput_{constructor_count}'].text)
                    constructor_count += 1
            # Building Upload
            contract = w3.eth.contract(abi=variables_test.abi, bytecode=variables_test.bytecode)
            print(f'Infura: {settings_test.infura_api}')
            # Alter Chain ID in case of Ganache Network active
            if settings_test.network == 'ganache':
                variables_test.nonce = w3.eth.getTransactionCount(settings_test.ganache_address)
                w3_balance = w3.eth.getTransactionCount(settings_test.ganache_address)
                print(f'Balance: {w3_balance}')
                variables_test.transaction = contract.constructor(*tuple(variables_test.constructor_inputs)).buildTransaction(
                    {'chainId': settings_test.ganache_id, "gasPrice": w3.eth.gasPrice,
                     'from': settings_test.ganache_address, 'nonce': variables_test.nonce})
                print(f'transaction: {variables_test.transaction}')
            # Of all networks are active
            else:
                variables_test.nonce = w3.eth.getTransactionCount(settings_test.address)
                print(f'chain ID: {settings_test.chain_id}')
                variables_test.transaction = contract.constructor(*tuple(variables_test.constructor_inputs)).buildTransaction(
                    {'chainId': settings_test.chain_id, "gasPrice": w3.eth.gasPrice, 'from': settings_test.address, 'nonce': variables_test.nonce})
                print(f'transaction: {variables_test.transaction}')
            # Gas Estimation
            variables_test.estimated_gas = w3.eth.estimateGas(variables_test.transaction)

            print(self.ids.GasEstimate.text)
            # Get ETH/USD Price
            variables_test.ethsc = Etherscan(settings_test.etherscan_api, net='main')
            variables_test.price = variables_test.ethsc.get_eth_last_price()
            variables_test.eth_price = variables_test.price['ethusd']
            variables_test.eth_price = round(float(variables_test.eth_price), 0)
            # Gas Price
            variables_test.gas_cost = float(w3.eth.gas_price / 1000000000)
            variables_test.gas_cost = round(float(variables_test.gas_cost), 3)
            gas_cost_usd = (variables_test.gas_cost / 1000000000) * variables_test.eth_price
            variables_test.upload_cost = variables_test.gas_cost * variables_test.estimated_gas

            variables_test.upload_cost_usd = (variables_test.upload_cost / 1000000000) * variables_test.eth_price
            variables_test.upload_cost_usd = round(float(variables_test.upload_cost_usd), 2)
            print(f'gas cost usd: {gas_cost_usd}')
            # Label write
            self.ids.GasEstimate.text = f'{variables_test.estimated_gas} units'
            self.ids.ETH_Price.text = f'{int(variables_test.eth_price)} USD'
            self.ids.GasCost.text = f'{variables_test.gas_cost} Gwei'
            self.ids.GasCostUSD.text = f"{str('{:f}'.format(gas_cost_usd))} USD"
            self.ids.UploadCost.text = f'{int(variables_test.upload_cost)} Gwei'
            self.ids.UploadCostUSD.text = f'{variables_test.upload_cost_usd} USD'
            print(self.ids.GasCost.text)
            print(f'Upload Cost: {variables_test.upload_cost_usd}')
            self.ids.Calculate.disabled = True
            self.ids.DeploySC.disabled = False
            self.ids.StatusBar.text = 'If displayed data are correct, hit "Deploy SC"'
        except web3.exceptions.ValidationError as e:
            self.ids.StatusBar.text = str(e)
        except requests.exceptions.ConnectionError as e:
            error = ''
            for l in str(e):
                if l != ':':
                    error = error + l
                else:
                    break
            self.ids.StatusBar.text = error
        except web3.exceptions.InvalidAddress as e:
            self.ids.StatusBar.text = f'{str(e)}'
        except requests.exceptions.HTTPError as e:
            self.ids.StatusBar.text = str(e)
        except ValueError as e:
            self.ids.StatusBar.text = str(e)
        except TypeError as e:
            self.ids.StatusBar.text = str(e)

    def deploy_sc(self):
        global w3

        signed_txn = ''

        try:
            # w3 declaration

            if settings_test.network != 'ganache':
                w3 = Web3(Web3.HTTPProvider(settings_test.infura_link))
                signed_txn = w3.eth.account.sign_transaction(variables_test.transaction, private_key=settings_test.private_key)
                self.ids.StatusBar.text = 'Signing transaction'
                self.ids.contract_webpage.disabled = False
            elif settings_test.network == 'ganache':
                # self.ganache_private_key_enter()
                try:
                    w3 = Web3(Web3.HTTPProvider(settings_test.ganache_rpc))
                    signed_txn = w3.eth.account.sign_transaction(variables_test.transaction, private_key=settings_test.ganache_private_key)
                    self.ids.StatusBar.text = 'Signing transaction'
                    self.ids.contract_webpage.disabled = True
                except TypeError:
                    self.ganache_private_key_popup()
                    return
            else:
                pass

            # Send transaction
            self.ids.StatusBar.text = 'Uploading SC'
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            variables_test.uploaded_sc = w3.eth.contract(address=tx_receipt.contractAddress, abi=variables_test.abi)
            variables_test.contract_address = tx_receipt.contractAddress
            # JSON update
            settings_test.last_contract = variables_test.contract_address
            print(f'Last contract: {settings_test.last_contract}')
            if settings_test.network == 'ganache':
                with open(f'{settings_test.last_contract}.json', 'w') as file:
                    json.dump(variables_test.compiled_contract, file, indent=1)
            if settings_test.network != 'mainnet':
                settings_test.contract_web_page = f'https://{settings_test.network}.etherscan.io/address/{variables_test.contract_address}'
            elif settings_test.network == 'ganache':
                pass
            else:
                settings_test.contract_web_page = f'https://etherscan.io/address/{variables_test.contract_address}'
            Settings.update_json(settings_test)
            # Enable/Disable Buttons
            self.ids.DeploySC.disabled = True
            # self.activate_uploaded_sc()
            self.transaction_cost_update()
            self.transaction_count()
            self.update_prices()
            self.ids.StatusBar.text = f'Contract deployed on: {variables_test.contract_address}'

            self.ids.copy_contract_address.disabled = False
        except binascii.Error as e:
            self.ids.StatusBar.text = str(e)
            print(e)
        except ValueError as e:
            self.ids.StatusBar.text = str(e)
            print(e)

    def set_compiler(self, state, compiler, version):

        self.ids.compiler_set.text = compiler
        settings_test.solidity_compiler = version
        settings_test.full_compiler = compiler

        Settings.update_json(settings_test)

    @staticmethod
    def open_webpage():
        webbrowser.open(settings_test.contract_web_page, new=2)

    # ################################################-Tab 1-################################################
    def activate_uploaded_sc(self):
        global w3

        try:
            variables_test.view_mutability = []
            variables_test.nonpayable_mutability = []
            variables_test.payable_mutability = []

            # w3 declaration
            if settings_test.network == 'ganache':
                w3 = Web3(Web3.HTTPProvider(settings_test.ganache_rpc))
                with open(f'{settings_test.last_contract}.json', 'w') as file:
                    json.dump(variables_test.compiled_contract, file, indent=1)
                print(f'sc file name: {variables_test.sc_file_name}')
                print(f'Subcontract: {variables_test.subcontract}')
                variables_test.contract_abi = variables_test.compiled_contract['contracts'][f'{variables_test.sc_file_name}'][f'{variables_test.subcontract}'][
                    'abi']

            else:
                w3 = Web3(Web3.HTTPProvider(settings_test.infura_link))
                variables_test.ethsc = Etherscan(settings_test.etherscan_api, net=settings_test.network)
                print(f'contract address: {variables_test.contract_address}')
                variables_test.contract_abi = variables_test.ethsc.get_contract_abi(variables_test.contract_address)
                variables_test.contract_abi = ast.literal_eval(variables_test.contract_abi)

            variables_test.contract_address = settings_test.last_contract
            # Contract Load Up
            variables_test.contract_address = Web3.toChecksumAddress(variables_test.contract_address)
            variables_test.uploaded_sc = w3.eth.contract(address=variables_test.contract_address, abi=variables_test.contract_abi)
            print(f'abi: {variables_test.contract_abi}')
            self.ids.StatusBar_1.text = f'Connected to {variables_test.contract_address}'
            # View Button creation
            for iterator, _ in enumerate(variables_test.contract_abi):
                print(f'lines: {variables_test.contract_abi[iterator]}')
                x = variables_test.contract_abi[iterator]
                for n in x:
                    print(f'sub: {x[n]}')
                    if x[n] == 'constructor':
                        variables_test.contract_abi.pop(iterator)

            for iterator, _ in enumerate(variables_test.contract_abi):
                # print(f'lines: {contract_abi[iterator]}')
                x = variables_test.contract_abi[iterator]
                for n in x:
                    # print(f'sub: {x[n]}')
                    if x[n] == 'constructor':
                        variables_test.contract_abi.pop(iterator)
                        continue
                    if x[n] == 'view':
                        variables_test.view_mutability.append(variables_test.contract_abi[iterator])
                    if x[n] == 'nonpayable':
                        variables_test.nonpayable_mutability.append(variables_test.contract_abi[iterator])
                    if x[n] == 'payable':
                        variables_test.payable_mutability.append(variables_test.contract_abi[iterator])

            for iterator, _ in enumerate(variables_test.view_mutability):
                print((variables_test.view_mutability[iterator]).get('name'))
                view_button = ViewButton(text=(variables_test.view_mutability[iterator]).get('name'))
                self.ids[f'{(variables_test.view_mutability[iterator]).get("name")}'] = view_button
                self.ids.view_buttons.add_widget(view_button)
                view_button.bind(on_release=partial(self.view_function_execution, view_button.text))

            for iterator, _ in enumerate(variables_test.nonpayable_mutability):
                print((variables_test.nonpayable_mutability[iterator]).get('name'))
                nonpayable_button = NonepayableButton(text=(variables_test.nonpayable_mutability[iterator]).get('name'))
                self.ids[f'{(variables_test.nonpayable_mutability[iterator]).get("name")}'] = nonpayable_button
                self.ids.nonpayable_buttons.add_widget(nonpayable_button)
                nonpayable_button.bind(on_release=partial(self.nonpayable_function_execution, nonpayable_button.text))

            for iterator, _ in enumerate(variables_test.payable_mutability):
                print((variables_test.payable_mutability[iterator]).get('name'))
                payable_button = PayableButton(text=(variables_test.payable_mutability[iterator]).get('name'))
                self.ids[f'{(variables_test.payable_mutability[iterator]).get("name")}'] = payable_button
                self.ids.payable_buttons.add_widget(payable_button)
                payable_button.bind(on_release=partial(self.payable_function_execution, payable_button.text))

            self.ids.UploadedSC.disabled = True
            self.ids.ExternalSC.disabled = True

        except AssertionError as e:
            self.ids.StatusBar_1.text = str(e)
            self.ids.ContractAddress.text = ''
        except ValueError:
            self.ids.StatusBar_1.text = f'Address Incorrect'
            self.ids.ContractAddress.text = ''

    def connect_to_sc(self):
        global w3
        try:
            variables_test.view_mutability = []
            variables_test.nonpayable_mutability = []
            variables_test.payable_mutability = []

            # w3 declaration
            if settings_test.network != 'ganache':
                w3 = Web3(Web3.HTTPProvider(settings_test.infura_link))
            else:
                w3 = Web3(Web3.HTTPProvider(settings_test.ganache_rpc))

            # Contract Load Up
            variables_test.ethsc = Etherscan(settings_test.etherscan_api, net=settings_test.network)
            variables_test.contract_address = str(self.ids.ContractAddress.text)
            variables_test.contract_address = Web3.toChecksumAddress(variables_test.contract_address)
            print(f'contract address: {variables_test.contract_address}')
            variables_test.contract_abi = variables_test.ethsc.get_contract_abi(variables_test.contract_address)
            variables_test.contract_abi = ast.literal_eval(variables_test.contract_abi)
            variables_test.uploaded_sc = w3.eth.contract(address=variables_test.contract_address, abi=variables_test.contract_abi)
            print(f'abi: {variables_test.contract_abi}')
            self.ids.StatusBar_1.text = f'Connected to {variables_test.contract_address}'

            # View Button creation
            for iterator, _ in enumerate(variables_test.contract_abi):
                print(f'lines: {variables_test.contract_abi[iterator]}')
                x = variables_test.contract_abi[iterator]
                for n in x:
                    print(f'sub: {x[n]}')
                    if x[n] == 'constructor':
                        variables_test.contract_abi.pop(iterator)

            for iterator, _ in enumerate(variables_test.contract_abi):
                print(f'k: {iterator}')
                x = variables_test.contract_abi[iterator]
                for n in x:
                    if x[n] == 'constructor':
                        variables_test.contract_abi.pop(iterator)
                        continue
                    if x[n] == 'view':
                        variables_test.view_mutability.append(variables_test.contract_abi[iterator])
                    if x[n] == 'nonpayable':
                        variables_test.nonpayable_mutability.append(variables_test.contract_abi[iterator])
                    if x[n] == 'payable':
                        variables_test.payable_mutability.append(variables_test.contract_abi[iterator])

            for iterator, _ in enumerate(variables_test.view_mutability):
                print((variables_test.view_mutability[iterator]).get('name'))
                view_button = ViewButton(text=(variables_test.view_mutability[iterator]).get('name'))
                self.ids[f'{(variables_test.view_mutability[iterator]).get("name")}'] = view_button
                self.ids.view_buttons.add_widget(view_button)
                view_button.bind(on_release=partial(self.view_function_execution, view_button.text))

            for iterator, _ in enumerate(variables_test.nonpayable_mutability):
                print((variables_test.nonpayable_mutability[iterator]).get('name'))
                nonpayable_button = NonepayableButton(text=(variables_test.nonpayable_mutability[iterator]).get('name'))
                self.ids[f'{(variables_test.nonpayable_mutability[iterator]).get("name")}'] = nonpayable_button
                self.ids.nonpayable_buttons.add_widget(nonpayable_button)
                nonpayable_button.bind(on_release=partial(self.nonpayable_function_execution, nonpayable_button.text))

            for iterator, _ in enumerate(variables_test.payable_mutability):
                print((variables_test.payable_mutability[iterator]).get('name'))
                payable_button = PayableButton(text=(variables_test.payable_mutability[iterator]).get('name'))
                self.ids[f'{(variables_test.payable_mutability[iterator]).get("name")}'] = payable_button
                self.ids.payable_buttons.add_widget(payable_button)
                payable_button.bind(on_release=partial(self.payable_function_execution, payable_button.text))

            self.ids.UploadedSC.disabled = True
            self.ids.ExternalSC.disabled = True
        except AssertionError as e:
            self.ids.StatusBar_1.text = str(e)
            self.ids.ContractAddress.text = ''
        except ValueError:
            self.ids.StatusBar_1.text = f'Address Incorrect'
            self.ids.ContractAddress.text = ''

        # view functions

    def view_function_execution(self, text, *args):

        view_function = ''
        variables_test.input_name = ''
        self.ids.output_layout.clear_widgets()
        self.ids.input_layout.clear_widgets()

        try:
            for iterator, _ in enumerate(variables_test.view_mutability):
                if text == variables_test.view_mutability[iterator].get('name'):
                    view_function = variables_test.view_mutability[iterator]
                    variables_test.input_name = variables_test.view_mutability[iterator].get('name')
                    print(view_function)
                    break
            # Output widgets
            variables_test.view_outputs = view_function.get('outputs')
            for iterator, _ in enumerate(variables_test.view_outputs):
                print(variables_test.view_outputs[iterator].get('name'))
                output_label = OutputLabel(text=f'{variables_test.view_outputs[iterator].get("name")}: ')
                self.ids[f'output_label_{iterator}'] = output_label
                self.ids.output_layout.add_widget(output_label)
            # Input widgets
            variables_test.view_inputs = view_function.get('inputs')
            print(f'View inputs: {variables_test.view_inputs}')
            if len(variables_test.view_inputs) != 0:
                for iterator, _ in enumerate(variables_test.view_inputs):
                    print(variables_test.view_inputs[iterator].get('name'))
                    input_label = InputLabel(text=f'{variables_test.view_inputs[iterator].get("name")}: ')
                    input_text = ClickInput(text=f'{variables_test.view_inputs[iterator].get("type")}')
                    self.ids[f'input_label_{iterator}'] = input_text
                    # Add widgets
                    self.ids.input_layout.add_widget(input_label)
                    self.ids.input_layout.add_widget(input_text)
                    # Enable execute button
                    self.ids.execute.disabled = False
                variables_test.distinguish = 'view'
            else:
                self.ids.execute.disabled = True
                print(f'input name: {variables_test.input_name}')
                print(f'uploaded SC: {variables_test.uploaded_sc}')
                if len(variables_test.view_outputs) == 1:
                    function_run = eval(f'variables_test.uploaded_sc.functions.{variables_test.input_name}().call()')
                    self.ids.output_label_0.text = f'{self.ids[f"output_label_0"].text} {function_run}'
                else:
                    for iterator, _ in enumerate(variables_test.view_outputs):
                        function_run = eval(f'variables_test.uploaded_sc.functions.{variables_test.input_name}().call()[{iterator}]')
                        self.ids[f"output_label_{iterator}"].text = f'{self.ids[f"output_label_{iterator}"].text} {function_run}'

        except web3.exceptions.ContractLogicError as e:
            self.ids.StatusBar_1.text = str(e)
            print(e)

    # Nonpayable function
    def nonpayable_function_execution(self, text, *args):
        global w3

        # Network Parameters
        variables_test.ethsc = Etherscan(settings_test.etherscan_api, net='main')
        # Get ETH/USD Price
        variables_test.price = variables_test.ethsc.get_eth_last_price()
        variables_test.eth_price = variables_test.price['ethusd']
        variables_test.eth_price = round(float(variables_test.eth_price), 0)
        variables_test.gas_price_usd = float()
        variables_test.gas_price = float()

        try:
            nonpayable_function = ''
            if settings_test.network != 'ganache':
                variables_test.my_address = settings_test.address
            else:
                variables_test.my_address = settings_test.ganache_address

            self.ids.calculate_transaction.disabled = True
            self.ids.output_layout.clear_widgets()
            self.ids.input_layout.clear_widgets()
            print(f'text: {text}')
            variables_test.function_name = text
            for iterator, _ in enumerate(variables_test.nonpayable_mutability):
                if text == variables_test.nonpayable_mutability[iterator].get('name'):
                    nonpayable_function = variables_test.nonpayable_mutability[iterator]
                    # print(f'nonpayable: {variables_test.nonpayable_function}')
                    break
            # Output widgets
            nonpayable_outputs = nonpayable_function.get('outputs')
            if len(nonpayable_outputs) != 0:
                for iterator, _ in enumerate(nonpayable_outputs):
                    print(f"nonpayable_name: {nonpayable_outputs[iterator].get('name')}")
                    output_label = OutputLabel(text=f'{nonpayable_outputs[iterator].get("name")}: ')
                    self.ids.output_layout.add_widget(output_label)
            else:
                pass
            # Input widgets
            variables_test.nonpayable_inputs = nonpayable_function.get('inputs')
            print(f'nonpayable inputs: {variables_test.nonpayable_inputs}')
            variables_test.distinguish = 'nonpayable'
            print(f'distinguish {variables_test.distinguish}')
            if len(variables_test.nonpayable_inputs) != 0:
                for iterator, _ in enumerate(variables_test.nonpayable_inputs):
                    print(variables_test.nonpayable_inputs[iterator].get('name'))
                    input_label = InputLabel(text=f'{variables_test.nonpayable_inputs[iterator].get("name")}:')
                    input_text = ClickInput(text=f'{variables_test.nonpayable_inputs[iterator].get("type")}')
                    self.ids[f'input_label_{iterator}'] = input_text
                    # Add widgets
                    self.ids.input_layout.add_widget(input_label)
                    self.ids.input_layout.add_widget(input_text)
                # Enable execute button
                self.ids.calculate_transaction.disabled = False
                self.ids.execute.disabled = True
                # Clear values
                self.clear_values()
            else:
                self.ids.execute.disabled = True
                variables_test.nonce = w3.eth.getTransactionCount(settings_test.address)
                # Create transaction
                variables_test.transaction = eval(f"variables_test.uploaded_sc.functions.{text}().buildTransaction")(
                    {'chainId': settings_test.chain_id, "gasPrice": w3.eth.gasPrice, 'from': variables_test.my_address, 'nonce': variables_test.nonce})
                # Transaction cost
                self.transaction_cost_update()
                # Execute button Enable
                self.ids.execute.disabled = False
        except web3.exceptions.ContractLogicError as e:
            self.ids.StatusBar_1.text = str(e)

        # Payable function

    def payable_function_execution(self, text, *args):
        global w3

        payable_function = ''
        variables_test.my_address = settings_test.address
        variables_test.amount_sent = int()

        variables_test.function_name = text

        self.ids.output_layout.clear_widgets()
        self.ids.input_layout.clear_widgets()

        for iterator, _ in enumerate(variables_test.payable_mutability):
            if text == variables_test.payable_mutability[iterator].get('name'):
                payable_function = variables_test.payable_mutability[iterator]
                print(payable_function)
                break
        # Output widgets
        payable_outputs = payable_function.get('outputs')
        if len(payable_outputs) != 0:
            for iterator, _ in enumerate(payable_outputs):
                print(payable_outputs[iterator].get('name'))
                output_label = OutputLabel(text=f'{payable_outputs[iterator].get("name")}: ')
                self.ids.output_layout.add_widget(output_label)
        else:
            pass
        # Input widgets
        variables_test.payable_inputs = payable_function.get('inputs')
        variables_test.distinguish = 'payable'
        print(f'distinguish {variables_test.distinguish}')
        print(variables_test.payable_inputs)
        if len(variables_test.payable_inputs) != 0:
            for iterator, _ in enumerate(variables_test.payable_inputs):
                print(variables_test.payable_inputs[iterator].get('name'))
                input_label = InputLabel(text=f'{variables_test.payable_inputs[iterator].get("name")}:')
                input_text = ClickInput(text=f'{variables_test.payable_inputs[iterator].get("type")}')
                self.ids[f'input_label_{iterator}'] = input_text
                # Add widgets
                self.ids.input_layout.add_widget(input_label)
                self.ids.input_layout.add_widget(input_text)
            # Enable execute button
            self.ids.calculate_transaction.disabled = False
            self.ids.execute.disabled = True
            # Clear values
            self.ids.gas_transaction.text = ''
            self.ids.gas_cost_transaction.text = ''
            self.ids.gas_cost_transaction_usd.text = ''
            self.ids.gwei_cost_transaction.text = ''
            self.ids.usd_cost_transaction.text = ''
        else:
            self.ids.calculate_transaction.disabled = False
            self.ids.execute.disabled = True
            variables_test.nonce = w3.eth.getTransactionCount(settings_test.address)
            try:
                # Create transaction
                variables_test.amount_sent = int(self.ids.currency_input.text)
                self.currency_conversion()
                variables_test.transaction = eval(f"variables_test.uploaded_sc.functions.{text}().buildTransaction")(
                    {'chainId': settings_test.ganache_id, "gasPrice": w3.eth.gasPrice,
                     'from': variables_test.my_address, 'nonce': variables_test.nonce, 'value': variables_test.amount_sent})
                # Transaction cost
                self.transaction_cost_update()
                # Execute button Enable
                self.ids.execute.disabled = False
            except web3.exceptions.ContractLogicError as e:
                self.ids.StatusBar_1.text = str(e)
                print(e)
            except ValueError:
                self.ids.StatusBar_1.test = 'Incorrect or no input into transacted amount'

    def calculate_transaction(self):

        function_inputs = []

        if variables_test.distinguish == 'nonpayable':
            try:
                for iterator, _ in enumerate(variables_test.nonpayable_inputs):
                    if not (self.ids[f'input_label_{iterator}'].text).isalpha():
                        n = int(self.ids[f'input_label_{iterator}'].text)
                        function_inputs.append(n)
                    else:
                        function_inputs.append(self.ids[f'input_label_{iterator}'].text)

                function_inputs = tuple(function_inputs)
                print(f'function inputs {function_inputs}')

                # Create transaction
                if settings_test.network == 'ganache':
                    variables_test.nonce = w3.eth.getTransactionCount(settings_test.ganache_address)
                    print(f'Ganache nonce: {variables_test.nonce}')
                    variables_test.transaction = eval(
                        f"variables_test.uploaded_sc.functions.{variables_test.function_name}(*function_inputs).buildTransaction")(
                        {'chainId': settings_test.ganache_id, "gasPrice": w3.eth.gasPrice, 'from': settings_test.ganache_address,
                         'nonce': int(variables_test.nonce)})
                else:
                    variables_test.nonce = w3.eth.getTransactionCount(settings_test.address)
                    variables_test.transaction = eval(
                        f"variables_test.uploaded_sc.functions.{variables_test.function_name}(*function_inputs).buildTransaction")(
                        {'chainId': settings_test.chain_id, "gasPrice": w3.eth.gasPrice, 'from': variables_test.my_address, 'nonce': int(variables_test.nonce)})
                    print(f'transaction: {variables_test.transaction}')
                # Transaction cost
                self.transaction_cost_update()
                # Execute button Enable
                self.ids.execute.disabled = False
            except web3.exceptions.ContractLogicError as e:
                self.ids.StatusBar_1.text = str(e)

        if variables_test.distinguish == 'payable':
            try:
                for iterator, _ in enumerate(variables_test.payable_inputs):
                    if (self.ids[f'input_label_{iterator}'].text).isnumeric():
                        n = int(self.ids[f'input_label_{iterator}'].text)
                        function_inputs.append(n)
                    else:
                        function_inputs.append(self.ids[f'input_label_{iterator}'].text)

                function_inputs = tuple(function_inputs)
                print(f'function inputs {function_inputs}')
                variables_test.nonce = w3.eth.getTransactionCount(settings_test.address)
                variables_test.amount_sent = float(self.ids.currency_input.text)
                self.currency_conversion()
                print(f'function name: {variables_test.function_name}')
                # Create transaction
                if settings_test.network == 'ganache':
                    variables_test.nonce = w3.eth.getTransactionCount(settings_test.ganache_address)
                    print(f'Ganache nonce: {variables_test.nonce}')
                    variables_test.transaction = eval(
                        f"variables_test.uploaded_sc.functions.{variables_test.function_name}(*function_inputs).buildTransaction")(
                        {'chainId': settings_test.ganache_id, "gasPrice": w3.eth.gasPrice,
                         'from': settings_test.ganache_address, 'nonce': variables_test.nonce, 'value': int(variables_test.amount_sent)})
                else:
                    variables_test.transaction = eval(
                        f"variables_test.uploaded_sc.functions.{variables_test.function_name}(*function_inputs).buildTransaction")(
                        {'chainId': settings_test.chain_id, "gasPrice": w3.eth.gasPrice,
                         'from': variables_test.my_address, 'nonce': variables_test.nonce, 'value': int(variables_test.amount_sent)})
                    print(f'transaction: {variables_test.transaction}')
                # Transaction cost
                self.transaction_cost_update()
                # Execute button Enable
                self.ids.execute.disabled = False
            except web3.exceptions.ContractLogicError as e:
                self.ids.StatusBar_1.text = str(e)

    def transact(self):
        global w3

        signed_store_txn = ''
        # View execution
        if variables_test.distinguish == 'view':

            function_inputs = []
            print(f'Input name: {variables_test.input_name}')
            try:
                for iterator, _ in enumerate(variables_test.view_inputs):
                    if not self.ids[f'input_label_{iterator}'].text.isalpha():
                        print('Int selected')
                        n = int(self.ids[f'input_label_{iterator}'].text)
                        function_inputs.append(n)
                    else:
                        print('Str selected')
                        function_inputs.append(self.ids[f'input_label_{iterator}'].text)

                function_inputs = tuple(function_inputs)
                print(f'function inputs {function_inputs}')
                if len(variables_test.view_outputs) == 1:
                    self.ids.output_label_0.text = f'{variables_test.view_outputs[0].get("name")}: '
                    function_run = eval(f'variables_test.uploaded_sc.functions.{variables_test.input_name}(*function_inputs).call()')
                    self.ids.output_label_0.text = f'{self.ids[f"output_label_0"].text} {function_run}'
                else:
                    for iterator, _ in enumerate(variables_test.view_outputs):
                        self.ids[f"output_label_{iterator}"].text = f'{variables_test.view_outputs[iterator].get("name")}: '
                        function_run = eval(f'variables_test.uploaded_sc.functions.{variables_test.input_name}(*function_inputs).call()[{iterator}]')
                        self.ids[
                            f"output_label_{iterator}"].text = f'{self.ids[f"output_label_{iterator}"].text} {function_run}'
                self.ids.StatusBar_1.text = f'Connected to {variables_test.contract_address}'

            except web3.exceptions.ValidationError as e:
                self.ids.StatusBar_1.text = 'Invalid Input'
                print(e)
            except ValueError as e:
                self.ids.StatusBar_1.text = 'Invalid Input'
                print(e)
        # Function execution
        # signed_store_txn = w3.eth.account.sign_transaction(variables_test.transaction, private_key=settings_test.private_key)
        else:
            if settings_test.network != 'ganache':
                w3 = Web3(Web3.HTTPProvider(settings_test.infura_link))
                signed_store_txn = w3.eth.account.sign_transaction(variables_test.transaction, private_key=settings_test.private_key)
                self.ids.StatusBar.text = 'Signing transaction'
            elif settings_test.network == 'ganache':
                # self.ganache_private_key_enter()
                try:
                    w3 = Web3(Web3.HTTPProvider(settings_test.ganache_rpc))
                    signed_store_txn = w3.eth.account.sign_transaction(variables_test.transaction, private_key=settings_test.ganache_private_key)
                    self.ids.StatusBar.text = 'Signing transaction'

                except TypeError as e:
                    self.ganache_private_key_popup_2()
                    print(e)
                    return

            send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
            w3.eth.wait_for_transaction_receipt(send_store_tx)
            self.transaction_count()
            self.update_prices()
            self.ids.calculate_transaction.disabled = True
            self.ids.execute.disabled = True
            self.clear_values()

    def currency_selection(self):
        if self.ids.currency_selection.text == 'Wei':
            self.ids.currency_selection.text = 'Gwei'
        elif self.ids.currency_selection.text == 'Gwei':
            self.ids.currency_selection.text = 'Ethereum'
        elif self.ids.currency_selection.text == 'Ethereum':
            self.ids.currency_selection.text = 'USD'
        elif self.ids.currency_selection.text == 'USD':
            self.ids.currency_selection.text = 'Wei'

    def clear_sc_address(self):

        variables_test.view_mutability = []
        variables_test.nonpayable_mutability = []
        variables_test.payable_mutability = []
        variables_test.contract_abi = ''
        self.ids.ContractAddress.text = ''
        self.ids.payable_buttons.clear_widgets()
        self.ids.nonpayable_buttons.clear_widgets()
        self.ids.view_buttons.clear_widgets()
        self.ids.input_layout.clear_widgets()
        self.ids.output_layout.clear_widgets()
        self.ids.StatusBar_1.text = 'Connect to SC'
        self.ids.UploadedSC.disabled = False
        self.ids.ExternalSC.disabled = False
        self.ids.calculate_transaction.disabled = True
        self.ids.execute.disabled = True
        self.ids.gas_transaction.text = ''
        self.ids.gas_cost_transaction.text = ''
        self.ids.gas_cost_transaction_usd.text = ''
        self.ids.gwei_cost_transaction.text = ''
        self.ids.usd_cost_transaction.text = ''

    def clear_values(self):

        # Clear values
        self.ids.gas_transaction.text = ''
        self.ids.gas_cost_transaction.text = ''
        self.ids.gas_cost_transaction_usd.text = ''
        self.ids.gwei_cost_transaction.text = ''
        self.ids.usd_cost_transaction.text = ''

    def currency_conversion(self):

        # Network Parameters
        variables_test.ethsc = Etherscan(settings_test.etherscan_api, net='main')
        # Get ETH/USD Price
        variables_test.price = variables_test.ethsc.get_eth_last_price()
        variables_test.eth_price = variables_test.price['ethusd']
        variables_test.eth_price = round(float(variables_test.eth_price), 0)

        if self.ids.currency_selection.text == 'Wei':
            pass
        elif self.ids.currency_selection.text == 'Gwei':
            variables_test.amount_sent = variables_test.amount_sent * 10 * 9
        elif self.ids.currency_selection.text == 'Ethereum':
            variables_test.amount_sent = variables_test.amount_sent * 10 ** 18
        elif self.ids.currency_selection.text == 'USD':
            variables_test.amount_sent = (variables_test.amount_sent / variables_test.eth_price) * 10 ** 18

    def transaction_cost_update(self):
        global w3

        # Network Parameters
        variables_test.ethsc = Etherscan(settings_test.etherscan_api, net='main')
        # Get ETH/USD Price
        variables_test.price = variables_test.ethsc.get_eth_last_price()
        variables_test.eth_price = variables_test.price['ethusd']
        variables_test.eth_price = round(float(variables_test.eth_price), 0)

        variables_test.gas_price_usd = float()
        variables_test.gas_price = float()

        # Gas Estimation
        variables_test.estimated_gas = w3.eth.estimateGas(variables_test.transaction)
        variables_test.gas_cost = float(w3.eth.gas_price / 1000000000)
        variables_test.gas_cost = round(float(variables_test.gas_cost), 3)
        # Gas cost in USD
        variables_test.gas_price_usd = float(variables_test.gas_cost) * 0.000000001 * float(variables_test.eth_price)
        # Transaction cost
        variables_test.upload_cost = variables_test.gas_cost * variables_test.estimated_gas
        variables_test.upload_cost = round(float(variables_test.upload_cost), 1)
        variables_test.upload_cost_usd = (variables_test.upload_cost / 1000000000) * variables_test.eth_price
        variables_test.upload_cost_usd = round(float(variables_test.upload_cost_usd), 2)

        print(f'Gas price USD: {variables_test.gas_cost}')
        self.ids.gas_transaction.text = f'{variables_test.estimated_gas} units'
        self.ids.gas_cost_transaction.text = f'{variables_test.gas_cost} Gwei'
        self.ids.gas_cost_transaction_usd.text = f"{str('{:f}'.format(variables_test.gas_price_usd))} USD"
        self.ids.gwei_cost_transaction.text = f'{variables_test.upload_cost} Gwei'
        self.ids.usd_cost_transaction.text = f'{variables_test.upload_cost_usd} USD'

    def address_cutting(self):

        if settings_test.network != 'ganache':
            short_address = settings_test.address
        else:
            short_address = settings_test.ganache_address

        short_address = short_address[:11]
        short_address = short_address + '...'
        self.ids.address_active.text = short_address
        self.ids.address_active_sc.text = short_address

    def transaction_count(self):

        print(f'ETH price: {variables_test.eth_price}')
        # Last gas spent
        self.ids.last_gas_spent.text = f'{variables_test.estimated_gas}'
        self.ids.last_gwei_spent.text = f'{int(variables_test.upload_cost)}'
        self.ids.last_usd_spent.text = f'{variables_test.upload_cost_usd}'
        self.ids.last_gas_spent_sc.text = f'{variables_test.estimated_gas}'
        self.ids.last_gwei_spent_sc.text = f'{int(variables_test.upload_cost)}'
        self.ids.last_usd_spent_sc.text = f'{variables_test.upload_cost_usd}'

        # Total gas spent
        self.ids.total_gas_used_sc.text = str(f'{float(self.ids.total_gas_used_sc.text) + float(self.ids.last_gas_spent_sc.text)}')
        self.ids.total_gwei_spent_sc.text = str(f'{float(self.ids.total_gwei_spent_sc.text) + float(self.ids.last_gwei_spent_sc.text)}')
        self.ids.total_usd_spent_sc.text = str(float(self.ids.total_usd_spent_sc.text) + float(self.ids.last_usd_spent_sc.text))
        self.ids.total_gwei_spent.text = str(float(self.ids.total_gwei_spent.text) + float(self.ids.last_gwei_spent.text))
        self.ids.total_usd_spent.text = str(float(self.ids.total_gwei_spent.text) + float(self.ids.last_usd_spent.text))

        settings_test.total_gas_used = f'{self.ids.total_gas_used_sc.text}'
        settings_test.total_gwei_spent = f'{self.ids.total_gwei_spent.text}'
        settings_test.total_usd_spent = f'{self.ids.total_usd_spent.text}'

        Settings.update_json(settings_test)

    def reset_gas_meter(self):

        # Total gas spent
        self.ids.total_gas_used_sc.text = '0'
        self.ids.total_gwei_spent_sc.text = '0'
        self.ids.total_usd_spent_sc.text = '0'
        self.ids.total_gwei_spent.text = '0'
        self.ids.total_usd_spent.text = '0'
        # Last gas spent
        self.ids.last_gas_spent.text = '0'
        self.ids.last_gwei_spent.text = '0'
        self.ids.last_usd_spent.text = '0'
        self.ids.last_gas_spent_sc.text = '0'
        self.ids.last_gwei_spent_sc.text = '0'
        self.ids.last_usd_spent_sc.text = '0'

        settings_test.total_gas_used = f'{self.ids.total_gas_used_sc.text}'
        settings_test.total_gwei_spent = f'{self.ids.total_gwei_spent.text}'
        settings_test.total_usd_spent = f'{self.ids.total_usd_spent.text}'

        Settings.update_json(settings_test)

    def ganache_address_balance(self, amount):
        print(f'Amount passed: {amount}')
        self.ids.Wallet_Balance.text = amount
        self.ids.active_network.text = 'Ganache'

    @staticmethod
    def ganache_private_key_enter(input):
        print(f'Private key: {input}')
        input = f'0x{input}'
        settings_test.ganache_private_key = input

    @staticmethod
    def ganache_private_key_popup():
        open_popup = PrivateKeyPopup()
        open_popup.open()

    @staticmethod
    def ganache_private_key_popup_2():
        open_popup = PrivateKeyPopup2()
        open_popup.open()

    def copy_contract_address(self):
        Clipboard.copy(settings_test.last_contract)
        self.ids.copy_contract_address.disabled = True
        if settings_test.network != 'mainnet':
            settings_test.contract_web_page = f'https://{settings_test.network}.etherscan.io/address/{settings_test.network}'
        elif settings_test.network == 'ganache':
            pass
        else:
            settings_test.contract_web_page = f'https://etherscan.io/address/{settings_test.network}'

    @staticmethod
    def test_focus(instance):
        if instance:
            print(f'Clicked on {instance}')
        else:
            print(f'Clicked off {instance}')


# #############################################-Class Setup-#############################################

class SmartContractOperationsApp(App):
    mylayout = MyLayout()

    def build(self):
        # self.popup_window = MyLayout()
        Window.clearcolor = (1, 166 / 255, 77 / 255, 1)
        return self.mylayout


if __name__ == '__main__':
    SmartContractOperationsApp().run()
