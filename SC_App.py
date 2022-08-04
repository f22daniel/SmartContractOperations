import ast
import binascii
import time
# from kivy.clock import Clock
import json
import threading

from functools import partial
import requests.exceptions
import solcx.exceptions
import web3
from etherscan import Etherscan
from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import *
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.tabbedpanel import *
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from plyer import filechooser
from solcx import compile_standard, install_solc
from web3 import Web3
from web3 import exceptions

# App variables
API = ''
ethsc = None
network = ''
price = None
eth_price = None
gas = None
gas_price = None
gas_price_wei = None
gas_price_usd = None
balance = None
conf_time = None
sc_file_path = ''
sc_file_name = ''
sc_file_keys = []
subcontract_name = []
short_address = ''

# SC variables
abi = ''
tx_hash = ''
my_address = ''
private_key = ''
chain_id = ''
contract_balance = ''
index = ''
bytecode = ''
contract_address = ''
compiled_contract = ''
constructor_inputs = []
w3 = ''
transaction = ''
uploaded_sc = ''
infura = ''
contract_abi = ''
iterator = 0
sub_iterator = 0
function = ''
variable = 1
view_mutability = []
payable_mutability = []
nonpayable_mutability = []
x = ''
input_name = ''
view_outputs = ''
view_inputs = ''
nonpayable_inputs = ''
payable_inputs = ''
function_inputs = ''
distinguish = ''
function_name = ''
nonce = ''
amount_sent = float()
estimated_gas = ''
gas_cost = ''
upload_cost = ''
upload_cost_usd = ''

Builder.load_file('SC_App.kv')
Window.size = (1100, 600)
settings = {'Address': '', 'Private Key': '', 'API': '', 'Infura': '', 'Gas Limit': '', 'Ganache Address': '',
            'Ganache ID': '', 'Mainnet': '', 'Goerli': '', 'Kovan': '', 'Rinkeby': '', 'Ropsten': '', 'Ganache': '',
            'Infura Link': '', 'Currency': '', 'Network': '', 'Solidity Compiler': '', 'Chain ID': '',
            'Last Contract': '', 'Ganache RPC': '', 'Ganache Private Key': '', 'Address 1_State': '', 'Address 2_State': '',
            'Address 3_State': '', 'Address 4_State': '', 'Address 5_State': '', 'Address 6_State': '',
            'Address 1': '', 'Address 2': '','Address 3': '', 'Address 4': '', 'Address 5': '', 'Address 6': '',
            'Private Key 1':'', 'Private Key 2':'', 'Private Key 3':'', 'Private Key 4':'', 'Private Key 5':'',
            'Private Key 6':'', 'Total Gas used': '', 'Total Gwei spent': '', 'Total USD spent': ''}

try:
    with open('settings.json', 'r') as f:
        data = json.loads(f.read())
    for x, y in data.items():
        settings.update({x: y})
except FileNotFoundError:
    pass


class MyLayout(TabbedPanel):

    def __init__(self, **kwargs):
        global API, network, ethsc, price, eth_price, gas, gas_price, gas_price_usd, balance, network, conf_time, \
            gas_price_wei, w3, chain_id, infura
        super().__init__(**kwargs)
        try:
            # Set up w3 protocol
            if settings.get('Network') != 'ganache':
                infura = settings.get('Infura Link')
                w3 = Web3(Web3.HTTPProvider(infura))
            else:
                w3 = Web3(Web3.HTTPProvider(settings.get('Ganache RPC')))

            # Get Wallet Balance
            if settings.get('Network') == 'ganache':
                w3_balance = w3.eth.getBalance(settings.get('Ganache Address'))
                w3_balance = f'{str(eval(f"{w3_balance}*0.000000000000000001"))}'
                w3_balance = round(float(w3_balance), 4)
                self.ids.Wallet_Balance.text = str(f'{w3_balance} ETH')
                self.ids.wallet_balance_sc.text = str(f'{w3_balance} ETH')
            else:
                balance = w3.eth.getBalance(f'{settings.get("Address")}')
                balance = f'{str(eval(f"{balance}*0.000000000000000001"))}'
                balance = round(float(balance), 4)
                self.ids.Wallet_Balance.text = str(f'{balance} ETH')
                self.ids.wallet_balance_sc.text = str(f'{balance} ETH')
                # print(self.ids.Wallet_Balance.text)

            # Network Parameters
            API = settings.get("API")
            network = settings.get('Network')
            ethsc = Etherscan(API, net='main')
            # Get ETH/USD Price
            price = ethsc.get_eth_last_price()
            eth_price = price['ethusd']
            eth_price = round(float(eth_price), 0)

            self.ids.ETH_Price.text = f'{int(eth_price)} USD'
            self.ids.eth_price_sc.text = f'{int(eth_price)} USD'
            # Get Gas Price
            gas = ethsc.get_gas_oracle()
            gas_price = gas['SafeGasPrice']
            gas_price_wei = int(gas_price) * 1000000000
            gas_price_usd = float(gas_price) * 0.000000001 * float(eth_price)
            self.ids.Gas_Price.text = f'{gas_price} Gwei'
            self.ids.Gas_Price_USD.text = f"{str('{:f}'.format(gas_price_usd))} USD"
            # Get conformation Time
            conf_time = ethsc.get_est_confirmation_time(gas_price_wei)
            self.ids.Conf_Time.text = f'{conf_time} s'
            # Currency selection
            self.ids.currency_selection.text = 'Wei'

            # Network Selection
            if settings['Mainnet'] == 'down':
                self.ids.Mainnet.state = 'down'
                self.ids.active_network.text = 'Mainnet'
                self.ids.network_active_sc.text = 'Mainnet'
                settings.update({'Network': 'main'})
                settings.update({'Infura Link': f'https://mainnet.infura.io/v3/{settings.get("Infura")}'})
                w3 = Web3(Web3.HTTPProvider(settings.get('Infura Link')))
                settings.update({'Chain ID': 1})
                chain_id = settings.get('Chain ID')
            if settings['Goerli'] == 'down':
                self.ids.Goerli.state = 'down'
                self.ids.active_network.text = 'Goerli'
                self.ids.network_active_sc.text = 'Goerli'
                settings.update({'Network': 'goerli'})
                settings.update({'Infura Link': f'https://goerli.infura.io/v3/{settings.get("Infura")}'})
                w3 = Web3(Web3.HTTPProvider(settings.get('Infura Link')))
                settings.update({'Chain ID': 5})
                chain_id = settings.get('Chain ID')
            if settings['Kovan'] == 'down':
                self.ids.Kovan.state = 'down'
                self.ids.active_network.text = 'Kovan'
                self.ids.network_active_sc.text = 'Kovan'
                settings.update({'Network': 'kovan'})
                settings.update({'Infura Link': f'https://kovan.infura.io/v3/{settings.get("Infura")}'})
                w3 = Web3(Web3.HTTPProvider(settings.get('Infura Link')))
                settings.update({'Chain ID': 42})
                chain_id = settings.get('Chain ID')
            if settings['Rinkeby'] == 'down':
                self.ids.Rinkeby.state = 'down'
                self.ids.active_network.text = 'Rinkeby'
                self.ids.network_active_sc.text = 'Rinkeby'
                settings.update({'Network': 'rinkeby'})
                settings.update({'Infura Link': f'https://rinkeby.infura.io/v3/{settings.get("Infura")}'})
                w3 = Web3(Web3.HTTPProvider(settings.get('Infura Link')))
                settings.update({'Chain ID': 4})
                chain_id = settings.get('Chain ID')
            if settings['Ropsten'] == 'down':
                self.ids.Ropsten.state = 'down'
                self.ids.active_network.text = 'Ropsten'
                self.ids.network_active_sc.text = 'Ropsten'
                settings.update({'Network': 'ropsten'})
                settings.update({'Infura Link': f'https://ropsten.infura.io/v3/{settings.get("Infura")}'})
                w3 = Web3(Web3.HTTPProvider(settings.get('Infura Link')))
                settings.update({'Chain ID': 3})
                chain_id = settings.get('Chain ID')
            if settings['Ganache'] == 'down':
                self.ids.Ganache.state = 'down'
                self.ids.active_network.text = 'Ganache'
                self.ids.network_active_sc.text = 'Ganache'
                settings.update({'Network': 'ganache'})
        except AssertionError as e:
            self.ids.StatusBar.text = str(e)
        except ValueError as e:
            self.ids.StatusBar.text = str(e)
        except requests.exceptions.ConnectionError as e:
            self.ids.StatusBar.text = str(e)
        # Settings
        self.ids.AddressEnter.text = settings['Address']
        self.ids.PrivateKeyEnter.text = settings['Private Key']
        self.ids.APIEnter.text = settings['API']
        self.ids.InfuraEnter.text = settings['Infura']
        self.ids.GasEnter.text = settings['Gas Limit']
        self.ids.GanacheRPCEnter.text = settings['Ganache RPC']
        self.ids.GanacheIDEnter.text = settings['Ganache ID']
        self.ids.SolidityCompiler.text = settings['Solidity Compiler']
        self.ids.GanacheAddressEnter.text = settings['Ganache Address']
        self.ids.GanachePrivateKeyEnter.text = settings['Ganache Private Key']
        self.ids.Address1.state = 'down'
        # Total gas spent
        self.ids.total_gas_used_sc.text = settings.get('Total Gas used')
        self.ids.total_gwei_spent_sc.text = settings.get('Total Gwei spent')
        self.ids.total_usd_spent_sc.text = settings.get('Total USD spent')
        self.ids.total_gas_used.text = settings.get('Total Gas used')
        self.ids.total_gwei_spent.text = settings.get('Total Gwei spent')
        self.ids.total_usd_spent.text = settings.get('Total USD spent')
        # Last gas spent
        self.ids.last_gas_spent.text = '0'
        self.ids.last_gwei_spent.text = '0'
        self.ids.last_usd_spent.text = '0'
        self.ids.last_gas_spent_sc.text = '0'
        self.ids.last_gwei_spent_sc.text = '0'
        self.ids.last_usd_spent_sc.text = '0'
        self.address_cutting()
        # Install solidity compiler
        install_solc(f'{self.ids.SolidityCompiler.text}')

    # ################################################-Tab 3-################################################
    # Settings Confirmation
    def address_enter(self, state):
        global data, settings, x, f
        if state is False:
            settings.update({'Address': f'{self.ids.AddressEnter.text}'})
            self.ids.AddressEnter.text = self.ids.AddressEnter.text.strip()
            self.address_cutting()
            for x in range(1, 7):
                if settings.get(f'Address {x}_State') == 'down':
                    settings.update({f'Address {x}': f'{self.ids.AddressEnter.text}'})
            with open('settings.json', 'w') as f:
                data = json.dumps(settings, indent=1)
                f.write(data)
            print('Saved')

    def private_key_enter(self, state):
        global data, f, x
        if state is False:
            settings.update({'Private Key': f'{self.ids.PrivateKeyEnter.text}'})
            self.ids.PrivateKeyEnter.text = self.ids.PrivateKeyEnter.text.strip()

            for x in range(1, 7):
                if settings.get(f'Address {x}_State') == 'down':
                    settings.update({f'Private Key {x}': f'{self.ids.PrivateKeyEnter.text}'})
            with open('settings.json', 'w') as f:
                data = json.dumps(settings, indent=1)
                f.write(data)
            print('Saved')

    def api_enter(self, state):
        global data, f, API, network, ethsc
        if state is False:
            settings.update({'API': f'{self.ids.APIEnter.text}'})
            self.ids.APIEnter.text = self.ids.APIEnter.text.strip()
            API = settings.get("API")
            if settings.get('Network') != 'ganache':
                ethsc = Etherscan(API, net=network)
            else:
                pass
            with open('settings.json', 'w') as f:
                data = json.dumps(settings, indent=1)
                f.write(data)
            print('Saved')

    def infura_enter(self, state):
        global data, f, w3
        if state is False:
            settings.update({'Infura': f'{self.ids.InfuraEnter.text}'})
            self.ids.InfuraEnter.text = self.ids.InfuraEnter.text.strip()
            infura_network = str.lower(self.ids.active_network.text)
            settings.update({'Infura Link': f'https://{infura_network}.infura.io/v3/{self.ids.InfuraEnter.text}'})
            w3 = Web3.HTTPProvider(settings.get('Infura Link'))
            with open('settings.json', 'w') as f:
                data = json.dumps(settings, indent=1)
                f.write(data)
            print('Saved')

    def gas_enter(self, state):
        global data, f
        if state is False:
            text = self.ids.GasEnter.text
            text = text.strip()
            try:
                int(text)
                settings.update({'Gas Limit': f'{self.ids.GasEnter.text}'})
                with open('settings.json', 'w') as f:
                    data = json.dumps(settings, indent=1)
                    f.write(data)
            except ValueError:
                self.ids.GasEnter.text = 'Error'
            print('Saved')

    def ganache_rpc_enter(self, state):
        global data, f
        if state is False:
            settings.update({'Ganache RPC': f'{self.ids.GanacheRPCEnter.text}'})
            self.ids.GanacheRPCEnter.text = self.ids.GanacheRPCEnter.text.strip()
            with open('settings.json', 'w') as f:
                data = json.dumps(settings, indent=1)
                f.write(data)
            print('Saved')

    def ganache_id_enter(self, state):
        global data, f
        if state is False:
            text = self.ids.GanacheIDEnter.text
            try:
                int(text)
                settings.update({'Ganache ID': f'{self.ids.GanacheIDEnter.text}'})
                with open('settings.json', 'w') as f:
                    data = json.dumps(settings, indent=1)
                    f.write(data)
            except ValueError:
                self.ids.GanacheIDEnter.text = 'Error'
            print('Saved')

    def solidity_compiler_enter(self, state):
        global data, f
        if state is False:
            settings.update({'Solidity Compiler': f'{self.ids.SolidityCompiler.text}'})
            self.ids.SolidityCompiler.text = self.ids.SolidityCompiler.text.strip()
            install_solc(f'{self.ids.SolidityCompiler.text}')
            with open('settings.json', 'w') as f:
                data = json.dumps(settings, indent=1)
                f.write(data)
            print('Saved')

    def ganache_address_enter(self, state):
        global data, f
        if state is False:
            settings.update({'Ganache Address': f'{self.ids.GanacheAddressEnter.text}'})
            self.ids.GanacheAddressEnter.text = self.ids.GanacheAddressEnter.text.strip()
            with open('settings.json', 'w') as f:
                data = json.dumps(settings, indent=1)
                f.write(data)
            print('Saved')

    def ganache_private_key_enter(self, state):
        global data, f
        if state is False:
            settings.update({'Ganache Private Key': f'{self.ids.GanachePrivateKeyEnter.text}'})
            self.ids.GanachePrivateKeyEnter.text = self.ids.GanachePrivateKeyEnter.text.strip()
            with open('settings.json', 'w') as f:
                data = json.dumps(settings, indent=1)
                f.write(data)
            print('Saved')

    #Active address selection
    def address_1(self):
        global settings
        if self.ids.Address1.state == 'down':
            settings.update({'Address 1_State': 'down'})
            settings.update({'Address 2_State': 'normal'})
            settings.update({'Address 3_State': 'normal'})
            settings.update({'Address 4_State': 'normal'})
            settings.update({'Address 5_State': 'normal'})
            settings.update({'Address 6_State': 'normal'})
            self.ids.Address2.state = 'normal'
            self.ids.Address3.state = 'normal'
            self.ids.Address4.state = 'normal'
            self.ids.Address5.state = 'normal'
            self.ids.Address6.state = 'normal'
            self.ids.AddressEnter.text = settings.get('Address 1')
            self.ids.PrivateKeyEnter.text = settings.get('Private Key 1')
            settings.update({'Address': f'{self.ids.AddressEnter.text}'})
            settings.update({'Private Key': f'{self.ids.PrivateKeyEnter.text}'})
            self.address_cutting()
            self.update_prices()

    def address_2(self):
        global settings
        if self.ids.Address2.state == 'down':
            settings.update({'Address 1_State': 'normal'})
            settings.update({'Address 2_State': 'down'})
            settings.update({'Address 3_State': 'normal'})
            settings.update({'Address 4_State': 'normal'})
            settings.update({'Address 5_State': 'normal'})
            settings.update({'Address 6_State': 'normal'})
            self.ids.Address1.state = 'normal'
            self.ids.Address3.state = 'normal'
            self.ids.Address4.state = 'normal'
            self.ids.Address5.state = 'normal'
            self.ids.Address6.state = 'normal'
            self.ids.AddressEnter.text = settings.get('Address 2')
            self.ids.PrivateKeyEnter.text = settings.get('Private Key 2')
            settings.update({'Address': f'{self.ids.AddressEnter.text}'})
            settings.update({'Private Key': f'{self.ids.PrivateKeyEnter.text}'})
            self.address_cutting()
            self.update_prices()

    def address_3(self):
        global settings
        if self.ids.Address3.state == 'down':
            settings.update({'Address 1_State': 'normal'})
            settings.update({'Address 2_State': 'normal'})
            settings.update({'Address 3_State': 'down'})
            settings.update({'Address 4_State': 'normal'})
            settings.update({'Address 5_State': 'normal'})
            settings.update({'Address 6_State': 'normal'})
            self.ids.Address2.state = 'normal'
            self.ids.Address1.state = 'normal'
            self.ids.Address4.state = 'normal'
            self.ids.Address5.state = 'normal'
            self.ids.Address6.state = 'normal'
            self.ids.AddressEnter.text = settings.get('Address 3')
            self.ids.PrivateKeyEnter.text = settings.get('Private Key 3')
            settings.update({'Address': f'{self.ids.AddressEnter.text}'})
            settings.update({'Private Key': f'{self.ids.PrivateKeyEnter.text}'})
            self.address_cutting()
            self.update_prices()

    def address_4(self):
        global settings
        if self.ids.Address4.state == 'down':
            settings.update({'Address 1_State': 'normal'})
            settings.update({'Address 2_State': 'normal'})
            settings.update({'Address 3_State': 'normal'})
            settings.update({'Address 4_State': 'down'})
            settings.update({'Address 5_State': 'normal'})
            settings.update({'Address 6_State': 'normal'})
            self.ids.Address2.state = 'normal'
            self.ids.Address3.state = 'normal'
            self.ids.Address1.state = 'normal'
            self.ids.Address5.state = 'normal'
            self.ids.Address6.state = 'normal'
            self.ids.AddressEnter.text = settings.get('Address 4')
            self.ids.PrivateKeyEnter.text = settings.get('Private Key 4')
            settings.update({'Address': f'{self.ids.AddressEnter.text}'})
            settings.update({'Private Key': f'{self.ids.PrivateKeyEnter.text}'})
            self.address_cutting()
            self.update_prices()

    def address_5(self):
        global settings
        if self.ids.Address5.state == 'down':
            settings.update({'Address 1_State': 'normal'})
            settings.update({'Address 2_State': 'normal'})
            settings.update({'Address 3_State': 'normal'})
            settings.update({'Address 4_State': 'normal'})
            settings.update({'Address 5_State': 'down'})
            settings.update({'Address 6_State': 'normal'})
            self.ids.Address2.state = 'normal'
            self.ids.Address3.state = 'normal'
            self.ids.Address4.state = 'normal'
            self.ids.Address1.state = 'normal'
            self.ids.Address6.state = 'normal'
            self.ids.AddressEnter.text = settings.get('Address 5')
            self.ids.PrivateKeyEnter.text = settings.get('Private Key 5')
            settings.update({'Address': f'{self.ids.AddressEnter.text}'})
            settings.update({'Private Key': f'{self.ids.PrivateKeyEnter.text}'})
            self.address_cutting()
            self.update_prices()

    def address_6(self):
        global settings
        if self.ids.Address6.state == 'down':
            settings.update({'Address 1_State': 'normal'})
            settings.update({'Address 2_State': 'normal'})
            settings.update({'Address 3_State': 'normal'})
            settings.update({'Address 4_State': 'normal'})
            settings.update({'Address 5_State': 'normal'})
            settings.update({'Address 6_State': 'down'})
            self.ids.Address2.state = 'normal'
            self.ids.Address3.state = 'normal'
            self.ids.Address4.state = 'normal'
            self.ids.Address5.state = 'normal'
            self.ids.Address1.state = 'normal'
            self.ids.AddressEnter.text = settings.get('Address 6')
            self.ids.PrivateKeyEnter.text = settings.get('Private Key 6')
            settings.update({'Address': f'{self.ids.AddressEnter.text}'})
            settings.update({'Private Key': f'{self.ids.PrivateKeyEnter.text}'})
            self.address_cutting()
            self.update_prices()

    # Network selection
    def mainnet_network(self):
        global data, f, network, ethsc, w3, chain_id, balance, settings, infura
        try:
            if self.ids.Mainnet.state == 'down':
                settings.update({'Mainnet': 'down'})
                settings.update({'Kovan': 'normal'})
                settings.update({'Goerli': 'normal'})
                settings.update({'Rinkeby': 'normal'})
                settings.update({'Ropsten': 'normal'})
                settings.update({'Ganache': 'normal'})
                self.ids.Goerli.state = 'normal'
                self.ids.Kovan.state = 'normal'
                self.ids.Rinkeby.state = 'normal'
                self.ids.Ropsten.state = 'normal'
                self.ids.Ganache.state = 'normal'
                self.ids.active_network.text = 'Mainnet'
                self.ids.network_active_sc.text = 'Mainnet'
                settings.update({'Infura Link': f'https://mainnet.infura.io/v3/{settings.get("Infura")}'})
                settings.update({'Network': 'main'})
                network = settings.get("Network")
                ethsc = Etherscan(API, net=network)
                infura = settings.get('Infura Link')
                w3 = Web3(Web3.HTTPProvider(infura))
                settings.update({'Chain ID': 1})
                chain_id = settings.get('Chain ID')
                balance = w3.eth.getBalance(f'{settings.get("Address")}')
                balance = f'{str(eval(f"{balance}*0.000000000000000001"))}'
                balance = round(float(balance), 5)
                self.ids.Wallet_Balance.text = str(f'{balance} ETH')
        except AssertionError as e:
            self.ids.StatusBar.text = str(e)
            self.ids.ETH_Price.text = 'N/A'
            self.ids.Gas_Price.text = 'N/A'
            self.ids.Gas_Price_USD.text = 'N/A'
            self.ids.Conf_Time.text = 'N/A'
        except requests.exceptions.ConnectionError:
            pass
        with open('settings.json', 'w') as f:
            data = json.dumps(settings, indent=1)
            f.write(data)

    def goerli_network(self):
        global data, f, network, ethsc, w3, chain_id, balance, settings, infura
        try:
            if self.ids.Goerli.state == 'down':
                settings.update({'Goerli': 'down'})
                settings.update({'Mainnet': 'normal'})
                settings.update({'Kovan': 'normal'})
                settings.update({'Rinkeby': 'normal'})
                settings.update({'Ropsten': 'normal'})
                settings.update({'Ganache': 'normal'})
                self.ids.Mainnet.state = 'normal'
                self.ids.Kovan.state = 'normal'
                self.ids.Rinkeby.state = 'normal'
                self.ids.Ropsten.state = 'normal'
                self.ids.Ganache.state = 'normal'
                self.ids.active_network.text = 'Goerli'
                self.ids.network_active_sc.text = 'Goerli'
                settings.update({'Infura Link': f'https://goerli.infura.io/v3/{settings.get("Infura")}'})
                settings.update({'Network': 'goerli'})
                network = settings.get("Network")
                ethsc = Etherscan(API, net=network)
                infura = settings.get('Infura Link')
                w3 = Web3(Web3.HTTPProvider(infura))
                settings.update({'Chain ID': 5})
                chain_id = settings.get('Chain ID')
                balance = w3.eth.getBalance(f'{settings.get("Address")}')
                balance = f'{str(eval(f"{balance}*0.000000000000000001"))}'
                balance = round(float(balance), 5)
                self.ids.Wallet_Balance.text = str(f'{balance} ETH')
        except AssertionError as e:
            self.ids.StatusBar.text = str(e)
            self.ids.ETH_Price.text = 'N/A'
            self.ids.Gas_Price.text = 'N/A'
            self.ids.Gas_Price_USD.text = 'N/A'
            self.ids.Conf_Time.text = 'N/A'
        except requests.exceptions.ConnectionError:
            pass
        with open('settings.json', 'w') as f:
            data = json.dumps(settings, indent=1)
            f.write(data)

    def kovan_network(self):
        global data, f, network, ethsc, w3, chain_id, balance, settings, infura
        try:
            if self.ids.Kovan.state == 'down':
                settings.update({'Kovan': 'down'})
                settings.update({'Mainnet': 'normal'})
                settings.update({'Goerli': 'normal'})
                settings.update({'Rinkeby': 'normal'})
                settings.update({'Ropsten': 'normal'})
                settings.update({'Ganache': 'normal'})
                self.ids.Mainnet.state = 'normal'
                self.ids.Goerli.state = 'normal'
                self.ids.Rinkeby.state = 'normal'
                self.ids.Ropsten.state = 'normal'
                self.ids.Ganache.state = 'normal'
                self.ids.active_network.text = 'Kovan'
                self.ids.network_active_sc.text = 'Kovan'
                settings.update({'Infura Link': f'https://kovan.infura.io/v3/{settings.get("Infura")}'})
                settings.update({'Network': 'kovan'})
                network = settings.get("Network")
                ethsc = Etherscan(API, net=network)
                infura = settings.get('Infura Link')
                w3 = Web3(Web3.HTTPProvider(infura))
                settings.update({'Chain ID': 42})
                chain_id = settings.get('Chain ID')
                balance = w3.eth.getBalance(f'{settings.get("Address")}')
                balance = f'{str(eval(f"{balance}*0.000000000000000001"))}'
                balance = round(float(balance), 5)
                self.ids.Wallet_Balance.text = str(f'{balance} ETH')
        except AssertionError as e:
            self.ids.StatusBar.text = str(e)
            self.ids.ETH_Price.text = 'N/A'
            self.ids.Gas_Price.text = 'N/A'
            self.ids.Gas_Price_USD.text = 'N/A'
            self.ids.Conf_Time.text = 'N/A'
        except requests.exceptions.ConnectionError:
            pass
        with open('settings.json', 'w') as f:
            data = json.dumps(settings, indent=1)
            f.write(data)

    def rinkeby_network(self):
        global data, f, network, ethsc, w3, chain_id, balance, settings, infura
        try:
            if self.ids.Rinkeby.state == 'down':
                settings.update({'Rinkeby': 'down'})
                settings.update({'Mainnet': 'normal'})
                settings.update({'Kovan': 'normal'})
                settings.update({'Goerli': 'normal'})
                settings.update({'Ropsten': 'normal'})
                settings.update({'Ganache': 'normal'})
                self.ids.Mainnet.state = 'normal'
                self.ids.Kovan.state = 'normal'
                self.ids.Goerli.state = 'normal'
                self.ids.Ropsten.state = 'normal'
                self.ids.Ganache.state = 'normal'
                self.ids.active_network.text = 'Rinkeby'
                self.ids.network_active_sc.text = 'Rinkeby'
                settings.update({'Infura Link': f'https://rinkeby.infura.io/v3/{settings.get("Infura")}'})
                settings.update({'Network': 'rinkeby'})
                network = settings.get("Network")
                ethsc = Etherscan(API, net=network)
                infura = settings.get('Infura Link')
                w3 = Web3(Web3.HTTPProvider(infura))
                settings.update({'Chain ID': 4})
                chain_id = settings.get('Chain ID')
                balance = w3.eth.getBalance(f'{settings.get("Address")}')
                balance = f'{str(eval(f"{balance}*0.000000000000000001"))}'
                balance = round(float(balance), 5)
                self.ids.Wallet_Balance.text = str(f'{balance} ETH')
        except AssertionError as e:
            self.ids.StatusBar.text = str(e)
            self.ids.ETH_Price.text = 'N/A'
            self.ids.Gas_Price.text = 'N/A'
            self.ids.Gas_Price_USD.text = 'N/A'
            self.ids.Conf_Time.text = 'N/A'
        except requests.exceptions.ConnectionError:
            pass
        with open('settings.json', 'w') as f:
            data = json.dumps(settings, indent=1)
            f.write(data)

    def ropsten_network(self):
        global data, f, network, ethsc, w3, chain_id, balance, settings, infura
        try:
            if self.ids.Ropsten.state == 'down':
                settings.update({'Ropsten': 'down'})
                settings.update({'Mainnet': 'normal'})
                settings.update({'Kovan': 'normal'})
                settings.update({'Rinkeby': 'normal'})
                settings.update({'Ganache': 'normal'})
                self.ids.Mainnet.state = 'normal'
                self.ids.Kovan.state = 'normal'
                self.ids.Rinkeby.state = 'normal'
                self.ids.Ganache.state = 'normal'
                self.ids.active_network.text = 'Ropsten'
                self.ids.network_active_sc.text = 'Ropsten'
                settings.update({'Infura Link': f'https://ropsten.infura.io/v3/{settings.get("Infura")}'})
                settings.update({'Network': 'ropsten'})
                network = settings.get("Network")
                ethsc = Etherscan(API, net=network)
                infura = settings.get('Infura Link')
                w3 = Web3(Web3.HTTPProvider(infura))
                settings.update({'Chain ID': 3})
                chain_id = settings.get('Chain ID')
                balance = w3.eth.getBalance(f'{settings.get("Address")}')
                balance = f'{str(eval(f"{balance}*0.000000000000000001"))}'
                balance = round(float(balance), 5)
                self.ids.Wallet_Balance.text = str(f'{balance} ETH')
        except AssertionError as e:
            self.ids.StatusBar.text = str(e)
            self.ids.ETH_Price.text = 'N/A'
            self.ids.Gas_Price.text = 'N/A'
            self.ids.Gas_Price_USD.text = 'N/A'
            self.ids.Conf_Time.text = 'N/A'
        except requests.exceptions.ConnectionError:
            pass
        with open('settings.json', 'w') as f:
            data = json.dumps(settings, indent=1)
            f.write(data)

    def ganache_network(self):
        global data, f, w3, settings
        try:
            if self.ids.Ganache.state == 'down':
                settings.update({'Ganache': 'down'})
                settings.update({'Mainnet': 'normal'})
                settings.update({'Kovan': 'normal'})
                settings.update({'Rinkeby': 'normal'})
                settings.update({'Ropsten': 'normal'})
                settings.update({'Goerli': 'normal'})
                self.ids.Mainnet.state = 'normal'
                self.ids.Kovan.state = 'normal'
                self.ids.Rinkeby.state = 'normal'
                self.ids.Ropsten.state = 'normal'
                self.ids.Goerli.state = 'normal'
                self.ids.active_network.text = 'Ganache'
                self.ids.network_active_sc.text = 'Ganache'
                settings.update({'Network': 'ganache'})
                ganache_rpc = settings.get('Ganache RPC')
                w3 = Web3(Web3.HTTPProvider(ganache_rpc))
                w3_balance = w3.eth.getBalance(settings.get('Ganache Address'))
                w3_balance = f'{str(eval(f"{w3_balance}*0.000000000000000001"))}'
                w3_balance = round(float(w3_balance), 4)
                self.ids.Wallet_Balance.text = str(f'{w3_balance} ETH')
        except web3.exceptions.InvalidAddress as e:
            self.ids.StatusBar.text = str(e)
        except AssertionError as e:
            self.ids.StatusBar.text = str(e)
            self.ids.ETH_Price.text = 'N/A'
            self.ids.Gas_Price.text = 'N/A'
            self.ids.Gas_Price_USD.text = 'N/A'
            self.ids.Conf_Time.text = 'N/A'
        except requests.exceptions.ConnectionError:
            pass
        with open('settings.json', 'w') as f:
            data = json.dumps(settings, indent=1)
            f.write(data)

    # ################################################-Tab 2-################################################
    def update_prices(self):
        global API, network, ethsc, price, eth_price, gas, gas_price, gas_price_usd, balance, network, gas_price_wei, \
            conf_time, infura, w3, infura
        try:
            '''
            # w3 declaration
            if settings.get('Network') != 'ganache':
                infura = settings.get('Infura Link')
                w3 = Web3(Web3.HTTPProvider(infura))
            else:
                w3 = Web3(Web3.HTTPProvider(settings.get('Ganache RPC')))
            '''
            # ETH Price update
            ethsc = Etherscan(API, net='main')
            price = ethsc.get_eth_last_price()
            eth_price = price['ethusd']
            eth_price = round(float(eth_price), 0)
            self.ids.ETH_Price.text = f'{int(eth_price)} USD'
            self.ids.eth_price_sc.text = f'{int(eth_price)} USD'
            print(self.ids.ETH_Price.text)
            # Gas Price update
            gas = ethsc.get_gas_oracle()
            gas_price = gas['SafeGasPrice']
            self.ids.Gas_Price.text = f'{gas_price} Gwei'
            print(self.ids.Gas_Price.text)
            # Gas Price USD update
            gas_price_usd = float(gas_price) * 0.000000001 * float(eth_price)
            self.ids.Gas_Price_USD.text = f"{str('{:f}'.format(gas_price_usd))} USD"
            print(self.ids.Gas_Price_USD.text)
            # Confirmation time update
            gas_price_wei = int(gas_price) * 1000000000
            conf_time = ethsc.get_est_confirmation_time(gas_price_wei)
            self.ids.Conf_Time.text = f'{conf_time} s'
            print(self.ids.Conf_Time.text)
            # Wallet Balance update
            if settings.get('Network') == 'ganache':
                w3_balance = w3.eth.getBalance(settings.get('Ganache Address'))
                w3_balance = f'{str(eval(f"{w3_balance}*0.000000000000000001"))}'
                w3_balance = round(float(w3_balance), 4)
                self.ids.Wallet_Balance.text = str(f'{w3_balance} ETH')
                self.ids.wallet_balance_sc.text = str(f'{balance} ETH')
            else:
                balance = w3.eth.getBalance(f'{settings.get("Address")}')
                balance = f'{str(eval(f"{balance}*0.000000000000000001"))}'
                balance = round(float(balance), 4)
                self.ids.Wallet_Balance.text = str(f'{balance} ETH')
                self.ids.wallet_balance_sc.text = str(f'{balance} ETH')
                print(self.ids.Wallet_Balance.text)
            self.ids.StatusBar.text = 'Ready to work'
        except AssertionError as e:
            self.ids.StatusBar.text = str(e)
            self.ids.ETH_Price.text = 'N/A'
            self.ids.Gas_Price.text = 'N/A'
            self.ids.Gas_Price_USD.text = 'N/A'
            self.ids.Conf_Time.text = 'N/A'

    # SC file selection
    def file_chooser(self):
        filechooser.open_file(on_selection=self.selected)
        self.ids.compile_sc.disabled = False
        self.ids.ChooseSC.disabled = True

    def selected(self, selection):
        global sc_file_path
        try:
            print(selection[0])
            sc_file_path = selection[0]
            self.ids.FilePath.text = sc_file_path
        except IndexError:
            pass

    def clear(self):
        global sc_file_path, sc_file_name, sc_file_keys, compiled_contract, constructor_inputs, subcontract_name
        self.ids.Constructor.clear_widgets()
        self.ids.FilePath.text = ''
        sc_file_path = ''
        sc_file_name = ''
        sc_file_keys = []
        compiled_contract = ''
        constructor_inputs = []
        subcontract_name = []
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

    def compile(self):
        global sc_file_path, compiled_contract, sc_file_name, bytecode, sc_file_keys, abi, constructor_inputs, \
            subcontract_name, iterator

        iterator = 0
        sc_file_name = ''

        # Open SC file
        try:
            with open(f'{sc_file_path}', "r") as file:
                sc_file = file.read()

            for i in reversed(sc_file_path):
                if i == '/':
                    break
                sc_file_name = i + sc_file_name

            print(f'SC file name: {sc_file_name}')
            # Compile SC
            compiled_contract = compile_standard(
                {
                    'language': 'Solidity',
                    'sources': {f'{sc_file_name}': {'content': sc_file}},
                    'settings': {
                        'outputSelection': {
                            '*': {'*': ['abi', 'metadata', 'evm.bytecode', 'evm.sourceMap']}
                        }
                    },
                }, solc_version=(settings.get('Solidity Compiler')))

            # Get SC_file_keys
            def get_all_keys(compiled_contract):
                for key, value in compiled_contract.items():
                    yield key
                    if isinstance(value, dict):
                        yield from get_all_keys(value)

            for j in get_all_keys(compiled_contract):
                sc_file_keys.append(j)
            print(f'sc_file_keys: {sc_file_keys}')
            # Get Subcontracts
            for _ in sc_file_keys:
                # print(sc_file_keys[iterator])
                if sc_file_keys[iterator] == 'abi':
                    subcontract_name.append(sc_file_keys[iterator - 1])
                    print(f'subcontracts: {subcontract_name}')
                iterator += 1
            iterator = 0
            # Enable/Disable buttons
            self.ids.compile_sc.disabled = True
            self.ids.select_sc.disabled = False
            # Create JSON file
            with open("compiled_code.json", "w") as file:
                json.dump(compiled_contract, file, indent=1)
            # Create Buttons
            for _ in subcontract_name:
                # Parametrise buttons
                new_toggle = SubContractButton(text=subcontract_name[iterator])
                # Add ID to buttons
                self.ids[subcontract_name[iterator]] = new_toggle
                new_toggle.bind(on_release=partial(self.select_subcontract, new_toggle.text))
                print(f'ToggleID: {self.ids[subcontract_name[iterator]]}')
                print(self.ids[subcontract_name[iterator]].state)
                iterator += 1
                # Create buttons
                self.ids.ContractSelection.add_widget(new_toggle)
            self.ids.select_sc.disabled = False
            self.ids.StatusBar.text = 'Select Subcontract!'
        except FileNotFoundError:
            self.ids.FilePath.text = 'File not found'
        except solcx.exceptions.SolcError:
            self.ids.StatusBar.text = 'Wrong compiler or incorrect syntax in Solidity file. Please check Settings or Contract'
            # solc_error = str(e)
            # print(f'{solc_error}')
        except AttributeError:
            pass

    def select_subcontract(self, text, *args):
        global sc_file_path, compiled_contract, sc_file_name, bytecode, sc_file_keys, abi, constructor_inputs, \
            subcontract_name, x

        constructor = []
        constructor_id = 0
        try:
            subcontract = text
            print(f'subcontract: {subcontract}')
            with open('compiled_code.json', 'r') as file:
                compiled_contract = json.loads(file.read())

            # Get Bytecode
            bytecode = compiled_contract['contracts'][f'{sc_file_name}'][f'{subcontract}']['evm']['bytecode'][
                'object']
            print(f'bytecode: {bytecode}')
            # Get ABI
            abi = compiled_contract['contracts'][f'{sc_file_name}'][f'{subcontract}']['abi']
            print(f'abi: {abi}')
            # Get Contructor
            for z in abi:
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
                    constructor_inputs.append(self.ids[f'ConstructorInput_{constructor_id}'].text)
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
        except KeyError:
            self.ids.StatusBar.text = 'Subcontract not selected!'

    def calculate_upload(self):
        global abi, bytecode, chain_id, constructor_inputs, w3, price, eth_price, ethsc, API, transaction, infura, nonce, estimated_gas, \
            gas_cost, upload_cost, upload_cost_usd

        try:
            constructor_count = 0
            ''''''
            # w3 declaration
            if settings.get('Network') != 'ganache':
                infura = settings.get('Infura Link')
                w3 = Web3(Web3.HTTPProvider(infura))
            else:
                w3 = Web3(Web3.HTTPProvider(settings.get('Ganache RPC')))
            print(f'abi: {abi}')
            print(f'bytecode: {bytecode}')

            for _ in constructor_inputs:
                if 'uint' in constructor_inputs[constructor_count]:
                    constructor_inputs[constructor_count] = int(self.ids[f'ConstructorInput_{constructor_count}'].text)
                    constructor_count += 1
                    print('uint')
                elif 'string' in constructor_inputs[constructor_count]:
                    constructor_inputs[constructor_count] = str(self.ids[f'ConstructorInput_{constructor_count}'].text)
                    constructor_count += 1
                # else:
                #     constructor_inputs[constructor_count] = self.ids[f'ConstructorInput_{constructor_count}'].text
                #     constructor_count += 1
            constructor_inputs = tuple(constructor_inputs)
            # Building Upload
            contract = w3.eth.contract(abi=abi, bytecode=bytecode)
            print('CHECKPOINT!!')
            print(f'Infura: {infura}')
            # Alter Chain ID in case of Ganache Network active
            if settings['Network'] == 'ganache':
                nonce = w3.eth.getTransactionCount(settings.get('Ganache Address'))
                chain_id = int(settings['Ganache ID'])
                print(f'chain ID: {chain_id}')
                w3_balance = w3.eth.getTransactionCount(settings.get('Ganache Address'))
                print(f'Balance: {w3_balance}')
                transaction = contract.constructor(*constructor_inputs).buildTransaction(
                    {'chainId': chain_id, "gasPrice": w3.eth.gasPrice,
                     'from': settings.get('Ganache Address'), 'nonce': nonce})
                print(f'transaction: {transaction}')
            # Of all networks are active
            else:
                nonce = w3.eth.getTransactionCount(settings.get('Address'))
                print(f'chain ID: {chain_id}')
                transaction = contract.constructor(*constructor_inputs).buildTransaction(
                    {'chainId': chain_id, "gasPrice": w3.eth.gasPrice, 'from': settings.get('Address'), 'nonce': nonce})
                print(f'transaction: {transaction}')
            # Gas Estimation
            estimated_gas = w3.eth.estimateGas(transaction)

            print(self.ids.GasEstimate.text)
            # Get ETH/USD Price
            ethsc = Etherscan(API, net='main')
            price = ethsc.get_eth_last_price()
            eth_price = price['ethusd']
            eth_price = round(float(eth_price), 0)
            # Gas Price
            gas_cost = float(w3.eth.gas_price / 1000000000)
            gas_cost = round(float(gas_cost), 3)
            gas_cost_usd = (gas_cost / 1000000000) * eth_price
            upload_cost = gas_cost * estimated_gas
            upload_cost_usd = (upload_cost / 1000000000) * eth_price
            upload_cost_usd = round(float(upload_cost_usd), 2)
            # Label write
            self.ids.GasEstimate.text = f'{estimated_gas} units'
            self.ids.ETH_Price.text = f'{int(eth_price)} USD'
            self.ids.GasCost.text = f'{gas_cost} Gwei'
            self.ids.GasCostUSD.text = f"{str('{:f}'.format(gas_cost_usd))} USD"
            self.ids.UploadCost.text = f'{int(upload_cost)} Gwei'
            self.ids.UploadCostUSD.text = f'{upload_cost_usd} USD'
            print(self.ids.GasCost.text)
            print(f'Upload Cost: {upload_cost_usd}')
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
        global abi, bytecode, chain_id, constructor_inputs, w3, price, eth_price, ethsc, API, transaction, \
            uploaded_sc, contract_address, settings, f, infura, data, private_key, balance
        try:
            # w3 declaration
            ''''''
            if settings.get('Network') != 'ganache':
                infura = settings.get('Infura Link')
                w3 = Web3(Web3.HTTPProvider(infura))
                private_key = settings.get('Private Key')
            else:
                w3 = Web3(Web3.HTTPProvider(settings.get('Ganache RPC')))
                private_key = settings.get('Ganache Private Key')

            # Sign transaction
            self.ids.StatusBar.text = 'Signing transaction'
            signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
            # Send transaction
            self.ids.StatusBar.text = 'Uploading SC'
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            uploaded_sc = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
            contract_address = tx_receipt.contractAddress
            print(f'Contract deployed on: {contract_address}')
            self.ids.StatusBar.text = f'Contract deployed on: {contract_address}'
            # JSON update
            settings.update({'Last Contract': f'{contract_address}'})
            print(f'Last contract: {settings.get("Last Contract")}')
            with open('settings.json', 'w') as f:
                data = json.dumps(settings, indent=1)
                f.write(data)
            # Wallet Balance update
            if settings.get('Network') == 'ganache':
                w3_balance = w3.eth.getBalance(settings.get('Ganache Address'))
                w3_balance = f'{str(eval(f"{w3_balance}*0.000000000000000001"))}'
                w3_balance = round(float(w3_balance), 4)
                self.ids.Wallet_Balance.text = str(f'{w3_balance} ETH')
                print('Checkpoint!!')
            else:
                ethsc = Etherscan(API, net=(settings.get('Network')))
                balance = ethsc.get_eth_balance(f'{settings.get("Address")}')
                balance = f'{str(eval(f"{balance}*0.000000000000000001"))}'
                balance = round(float(balance), 4)
                self.ids.Wallet_Balance.text = str(f'{balance} ETH')
                print(self.ids.Wallet_Balance.text)
            # Enable/Disable Buttons
            self.ids.DeploySC.disabled = True
            # self.activate_uploaded_sc()
            self.transaction_count()
            self.update_prices()
            self.ids.StatusBar.text = f'Contract deployed on: {contract_address}'
        except binascii.Error as e:
            self.ids.StatusBar.text = str(e)
        except ValueError as e:
            self.ids.StatusBar.text = str(e)

    # ################################################-Tab 1-################################################
    def activate_uploaded_sc(self):
        global settings, ethsc, API, network, contract_address, contract_abi, iterator, x, view_mutability, \
            nonpayable_mutability, payable_mutability, infura, w3, uploaded_sc, ethsc

        try:
            iterator = 0
            view_mutability = []
            nonpayable_mutability = []
            payable_mutability = []
            ''''''
            # w3 declaration
            if settings.get('Network') != 'ganache':
                infura = settings.get('Infura Link')
                w3 = Web3(Web3.HTTPProvider(infura))
            else:
                w3 = Web3(Web3.HTTPProvider(settings.get('Ganache RPC')))

            # Contract Load Up
            API = settings.get("API")
            network = settings.get('Network')
            ethsc = Etherscan(API, net=network)
            contract_address = settings.get('Last Contract')
            print(f'contract address: {contract_address}')
            contract_abi = ethsc.get_contract_abi(contract_address)
            contract_abi = ast.literal_eval(contract_abi)
            contract_address = Web3.toChecksumAddress(contract_address)
            uploaded_sc = w3.eth.contract(address=contract_address, abi=contract_abi)
            print(f'abi: {contract_abi}')
            self.ids.StatusBar_1.text = f'Connected to {contract_address}'
            # View Button creation
            for _ in contract_abi:
                print(f'lines: {contract_abi[iterator]}')
                x = contract_abi[iterator]
                for n in x:
                    print(f'sub: {x[n]}')
                    if x[n] == 'constructor':
                        contract_abi.pop(iterator)
                iterator += 1

            iterator = 0

            for _ in contract_abi:
                # print(f'lines: {contract_abi[iterator]}')
                x = contract_abi[iterator]
                for n in x:
                    # print(f'sub: {x[n]}')
                    if x[n] == 'constructor':
                        contract_abi.pop(iterator)
                        continue
                    if x[n] == 'view':
                        view_mutability.append(contract_abi[iterator])
                    if x[n] == 'nonpayable':
                        nonpayable_mutability.append(contract_abi[iterator])
                    if x[n] == 'payable':
                        payable_mutability.append(contract_abi[iterator])
                iterator += 1

            iterator = 0
            for _ in view_mutability:
                print((view_mutability[iterator]).get('name'))
                view_button = ViewButton(text=(view_mutability[iterator]).get('name'))
                self.ids[f'{(view_mutability[iterator]).get("name")}'] = view_button
                self.ids.view_buttons.add_widget(view_button)
                view_button.bind(on_release=partial(self.view_function_execution, view_button.text))
                iterator += 1

            iterator = 0

            for _ in nonpayable_mutability:
                print((nonpayable_mutability[iterator]).get('name'))
                nonpayable_button = NonepayableButton(text=(nonpayable_mutability[iterator]).get('name'))
                self.ids[f'{(nonpayable_mutability[iterator]).get("name")}'] = nonpayable_button
                self.ids.nonpayable_buttons.add_widget(nonpayable_button)
                nonpayable_button.bind(on_release=partial(self.nonpayable_function_execution, nonpayable_button.text))
                iterator += 1

            iterator = 0

            for _ in payable_mutability:
                print((payable_mutability[iterator]).get('name'))
                payable_button = PayableButton(text=(payable_mutability[iterator]).get('name'))
                self.ids[f'{(payable_mutability[iterator]).get("name")}'] = payable_button
                self.ids.payable_buttons.add_widget(payable_button)
                payable_button.bind(on_release=partial(self.payable_function_execution, payable_button.text))
                iterator += 1

            self.ids.UploadedSC.disabled = True
            self.ids.ExternalSC.disabled = True

        except AssertionError as e:
            self.ids.StatusBar_1.text = str(e)

    def connect_to_sc(self):
        global ethsc, API, network, function, variable, view_mutability, payable_mutability, uploaded_sc, \
            nonpayable_mutability, API, network, settings, contract_address, contract_abi, iterator, x, w3, infura, \
            input_name

        iterator = 0
        view_mutability = []
        nonpayable_mutability = []
        payable_mutability = []

        ''''''
        # w3 declaration
        if settings.get('Network') != 'ganache':
            infura = settings.get('Infura Link')
            w3 = Web3(Web3.HTTPProvider(infura))
        else:
            w3 = Web3(Web3.HTTPProvider(settings.get('Ganache RPC')))
        print('Checkpoint!!')

        # Contract Load Up
        try:
            API = settings.get("API")
            network = settings.get('Network')
            ethsc = Etherscan(API, net=network)
            contract_address = str(self.ids.ContractAddress.text)
            contract_address = Web3.toChecksumAddress(contract_address)
            print(f'contract address: {contract_address}')
            contract_abi = ethsc.get_contract_abi(contract_address)
            contract_abi = ast.literal_eval(contract_abi)
            uploaded_sc = w3.eth.contract(address=contract_address, abi=contract_abi)

            print(f'abi: {contract_abi}')
            self.ids.StatusBar_1.text = f'Connected to {contract_address}'
        except AssertionError as e:
            self.ids.StatusBar_1.text = str(e)
            self.ids.ContractAddress.text = ''
        except ValueError:
            self.ids.StatusBar_1.text = f'Address Incorrect'
            self.ids.ContractAddress.text = ''
        # View Button creation
        for _ in contract_abi:
            print(f'lines: {contract_abi[iterator]}')
            x = contract_abi[iterator]
            for n in x:
                print(f'sub: {x[n]}')
                if x[n] == 'constructor':
                    contract_abi.pop(iterator)
            iterator += 1

        iterator = 0

        for _ in contract_abi:
            # print(f'lines: {contract_abi[iterator]}')
            x = contract_abi[iterator]
            for n in x:
                # print(f'sub: {x[n]}')
                if x[n] == 'constructor':
                    contract_abi.pop(iterator)
                    continue
                if x[n] == 'view':
                    view_mutability.append(contract_abi[iterator])
                if x[n] == 'nonpayable':
                    nonpayable_mutability.append(contract_abi[iterator])
                if x[n] == 'payable':
                    payable_mutability.append(contract_abi[iterator])
            iterator += 1

        iterator = 0

        for _ in view_mutability:
            print((view_mutability[iterator]).get('name'))
            view_button = ViewButton(text=(view_mutability[iterator]).get('name'))
            self.ids[f'{(view_mutability[iterator]).get("name")}'] = view_button
            self.ids.view_buttons.add_widget(view_button)
            view_button.bind(on_release=partial(self.view_function_execution, view_button.text))
            iterator += 1

        iterator = 0

        for _ in nonpayable_mutability:
            print((nonpayable_mutability[iterator]).get('name'))
            nonpayable_button = NonepayableButton(text=(nonpayable_mutability[iterator]).get('name'))
            self.ids[f'{(nonpayable_mutability[iterator]).get("name")}'] = nonpayable_button
            self.ids.nonpayable_buttons.add_widget(nonpayable_button)
            nonpayable_button.bind(on_release=partial(self.nonpayable_function_execution, nonpayable_button.text))
            iterator += 1

        iterator = 0

        for _ in payable_mutability:
            print((payable_mutability[iterator]).get('name'))
            payable_button = PayableButton(text=(payable_mutability[iterator]).get('name'))
            self.ids[f'{(payable_mutability[iterator]).get("name")}'] = payable_button
            self.ids.payable_buttons.add_widget(payable_button)
            payable_button.bind(on_release=partial(self.payable_function_execution, payable_button.text))
            iterator += 1

        self.ids.UploadedSC.disabled = True
        self.ids.ExternalSC.disabled = True

        # view functions

    def view_function_execution(self, text, *args):
        global iterator, view_mutability, uploaded_sc, input_name, view_outputs, view_inputs, distinguish

        view_function = ''
        input_name = ''
        iterator = 0
        self.ids.output_layout.clear_widgets()
        self.ids.input_layout.clear_widgets()

        try:
            for _ in view_mutability:
                if text == view_mutability[iterator].get('name'):
                    view_function = view_mutability[iterator]
                    input_name = view_mutability[iterator].get('name')
                    print(view_function)
                    break
                iterator += 1
            # Output widgets
            iterator = 0
            view_outputs = view_function.get('outputs')
            for _ in view_outputs:
                print(view_outputs[iterator].get('name'))
                output_label = OutputLabel(text=f'{view_outputs[iterator].get("name")}: ')
                self.ids[f'output_label_{iterator}'] = output_label
                self.ids.output_layout.add_widget(output_label)
                iterator += 1
            # Input widgets
            iterator = 0
            view_inputs = view_function.get('inputs')
            print(f'View inputs: {view_inputs}')
            if len(view_inputs) != 0:
                for _ in view_inputs:
                    print(view_inputs[iterator].get('name'))
                    input_label = InputLabel(text=f'{view_inputs[iterator].get("name")}: ')
                    input_text = ClickInput(text=f'{view_inputs[iterator].get("type")}')
                    self.ids[f'input_label_{iterator}'] = input_text
                    # Add widgets
                    self.ids.input_layout.add_widget(input_label)
                    self.ids.input_layout.add_widget(input_text)
                    # Enable execute button
                    self.ids.execute.disabled = False
                    iterator += 1
                distinguish = 'view'
            else:
                self.ids.execute.disabled = True
                print(f'input name: {input_name}')
                print(f'uploaded SC: {uploaded_sc}')
                if len(view_outputs) == 1:
                    function_run = eval(f'uploaded_sc.functions.{input_name}().call()')
                    self.ids.output_label_0.text = f'{self.ids[f"output_label_0"].text} {function_run}'
                else:
                    iterator = 0
                    for _ in view_outputs:
                        function_run = eval(f'uploaded_sc.functions.{input_name}().call()[{iterator}]')
                        self.ids[
                            f"output_label_{iterator}"].text = f'{self.ids[f"output_label_{iterator}"].text} {function_run}'
                        iterator += 1
        except web3.exceptions.ContractLogicError as e:
            self.ids.StatusBar_1.text = str(e)

    # Nonpayable function
    def nonpayable_function_execution(self, text, *args):
        global iterator, my_address, w3, uploaded_sc, chain_id, eth_price, ethsc, price, API, gas_price_usd, \
            gas_price, distinguish, nonpayable_inputs, function_name, transaction, nonce

        # Network Parameters
        API = settings.get("API")
        ethsc = Etherscan(API, net='main')
        # Get ETH/USD Price
        price = ethsc.get_eth_last_price()
        eth_price = price['ethusd']
        eth_price = round(float(eth_price), 0)
        gas_price_usd = float()
        gas_price = float()

        try:
            iterator = 0
            nonpayable_function = ''
            if settings.get('Network') != 'ganache':
                my_address = settings.get('Address')
            else:
                my_address = settings.get('Ganache Address')

            self.ids.calculate_transaction.disabled = True
            self.ids.output_layout.clear_widgets()
            self.ids.input_layout.clear_widgets()
            print(f'text: {text}')
            function_name = text
            for _ in nonpayable_mutability:
                if text == nonpayable_mutability[iterator].get('name'):
                    nonpayable_function = nonpayable_mutability[iterator]
                    print(f'nonpayable: {nonpayable_function}')
                    break
                iterator += 1
            # Output widgets
            iterator = 0
            nonpayable_outputs = nonpayable_function.get('outputs')
            if len(nonpayable_outputs) != 0:
                for _ in nonpayable_outputs:
                    print(f"nonpayable_name: {nonpayable_outputs[iterator].get('name')}")
                    output_label = OutputLabel(text=f'{nonpayable_outputs[iterator].get("name")}: ')
                    self.ids.output_layout.add_widget(output_label)
                    iterator += 1
            else:
                pass
            # Input widgets
            iterator = 0
            nonpayable_inputs = nonpayable_function.get('inputs')
            print(f'nonpayable inputs: {nonpayable_inputs}')
            distinguish = 'nonpayable'
            print(f'distinguish {distinguish}')
            if len(nonpayable_inputs) != 0:
                for _ in nonpayable_inputs:
                    print(nonpayable_inputs[iterator].get('name'))
                    input_label = InputLabel(text=f'{nonpayable_inputs[iterator].get("name")}:')
                    input_text = ClickInput(text=f'{nonpayable_inputs[iterator].get("type")}')
                    self.ids[f'input_label_{iterator}'] = input_text
                    # Add widgets
                    self.ids.input_layout.add_widget(input_label)
                    self.ids.input_layout.add_widget(input_text)

                    iterator += 1
                # Enable execute button
                self.ids.calculate_transaction.disabled = False
                self.ids.execute.disabled = True
                # Clear values
                self.clear_values()
            else:
                self.ids.execute.disabled = True
                nonce = w3.eth.getTransactionCount(settings.get('Address'))
                # Create transaction
                transaction = eval(f"uploaded_sc.functions.{text}().buildTransaction")(
                    {'chainId': chain_id, "gasPrice": w3.eth.gasPrice, 'from': my_address, 'nonce': nonce})
                # Transaction cost
                self.transaction_cost_update()
                # Execute button Enable
                self.ids.execute.disabled = False
        except web3.exceptions.ContractLogicError as e:
            self.ids.StatusBar_1.text = str(e)

        # Payable function
    def payable_function_execution(self, text, *args):
        global iterator, my_address, w3, uploaded_sc, chain_id, eth_price, ethsc, price, API, gas_price_usd, \
            gas_price, distinguish, function_name, transaction, nonce, payable_inputs, amount_sent, my_address

        iterator = 0
        payable_function = ''
        my_address = settings.get('Address')
        amount_sent = float()

        function_name = text

        self.ids.output_layout.clear_widgets()
        self.ids.input_layout.clear_widgets()

        for _ in payable_mutability:
            if text == payable_mutability[iterator].get('name'):
                payable_function = payable_mutability[iterator]
                print(payable_function)
                break
            iterator += 1
        # Output widgets
        iterator = 0
        payable_outputs = payable_function.get('outputs')
        if len(payable_outputs) != 0:
            for _ in payable_outputs:
                print(payable_outputs[iterator].get('name'))
                output_label = OutputLabel(text=f'{payable_outputs[iterator].get("name")}: ')
                self.ids.output_layout.add_widget(output_label)
                iterator += 1
        else:
            pass
        # Input widgets
        iterator = 0
        payable_inputs = payable_function.get('inputs')
        distinguish = 'payable'
        print(f'distinguish {distinguish}')
        print(payable_inputs)
        if len(payable_inputs) != 0:
            for _ in payable_inputs:
                print(payable_inputs[iterator].get('name'))
                input_label = InputLabel(text=f'{payable_inputs[iterator].get("name")}:')
                input_text = ClickInput(text=f'{payable_inputs[iterator].get("type")}')
                self.ids[f'input_label_{iterator}'] = input_text
                # Add widgets
                self.ids.input_layout.add_widget(input_label)
                self.ids.input_layout.add_widget(input_text)

                iterator += 1
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
            self.ids.execute.disabled = True
            nonce = w3.eth.getTransactionCount(settings.get('Address'))
            try:
                # Create transaction
                amount_sent = float(self.ids.currency_input.text)
                self.currency_conversion()
                print(f'amount sent: {amount_sent}')
                transaction = eval(f"uploaded_sc.functions.{text}().buildTransaction")(
                    {'chainId': chain_id, "gasPrice": w3.eth.gasPrice,
                     'from': my_address, 'nonce': nonce, 'value': amount_sent})
                # Transaction cost
                self.transaction_cost_update()
                # Execute button Enable
                self.ids.execute.disabled = False
            except web3.exceptions.ContractLogicError as e:
                self.ids.StatusBar_1.text = str(e)
            except ValueError:
                self.ids.StatusBar_1.test = 'Incorrect or no input into transacted amount'

    def calculate_transaction(self):
        global iterator, distinguish, function_name, gas_price_usd, function_inputs, nonpayable_inputs, transaction, \
            nonce, payable_inputs, amount_sent

        function_inputs = []
        iterator = 0

        if distinguish == 'nonpayable':
            try:
                for _ in nonpayable_inputs:
                    if not (self.ids[f'input_label_{iterator}'].text).isalpha():
                        n = int(self.ids[f'input_label_{iterator}'].text)
                        function_inputs.append(n)
                        iterator += 1
                    else:
                        function_inputs.append(self.ids[f'input_label_{iterator}'].text)
                        iterator += 1

                function_inputs = tuple(function_inputs)
                print(f'function inputs {function_inputs}')
                nonce = w3.eth.getTransactionCount(settings.get('Address'))
                # Create transaction
                transaction = eval(f"uploaded_sc.functions.{function_name}(*function_inputs).buildTransaction")(
                    {'chainId': chain_id, "gasPrice": w3.eth.gasPrice, 'from': my_address, 'nonce': nonce})
                print(f'transaction: {transaction}')
                # Transaction cost
                self.transaction_cost_update()
                # Execute button Enable
                self.ids.execute.disabled = False
            except web3.exceptions.ContractLogicError as e:
                self.ids.StatusBar_1.text = str(e)

        if distinguish == 'payable':
            try:
                for _ in payable_inputs:
                    if not (self.ids[f'input_label_{iterator}'].text).isalpha():
                        n = int(self.ids[f'input_label_{iterator}'].text)
                        function_inputs.append(n)
                        iterator += 1
                    else:
                        function_inputs.append(self.ids[f'input_label_{iterator}'].text)
                        iterator += 1

                function_inputs = tuple(function_inputs)
                print(f'function inputs {function_inputs}')
                nonce = w3.eth.getTransactionCount(settings.get('Address'))
                amount_sent = float(self.ids.currency_input.text)
                self.currency_conversion()
                print(f'amount sent: {amount_sent}')
                print(f'function name: {function_name}')
                # Create transaction
                transaction = eval(f"uploaded_sc.functions.{function_name}(*function_inputs).buildTransaction")(
                    {'chainId': chain_id, "gasPrice": w3.eth.gasPrice,
                     'from': my_address, 'nonce': nonce, 'value': amount_sent})
                print(f'transaction: {transaction}')
                # Transaction cost
                self.transaction_cost_update()
                # Execute button Enable
                self.ids.execute.disabled = False
            except web3.exceptions.ContractLogicError as e:
                self.ids.StatusBar_1.text = str(e)

    def transact(self):
        global iterator, input_name, uploaded_sc, view_outputs, view_inputs, function_inputs, contract_address, \
            distinguish, w3, nonpayable_inputs, private_key, transaction, nonce, amount_sent

        iterator = 0
        private_key = settings.get('Private Key')
        # View execution
        if distinguish == 'view':

            function_inputs = []
            print(f'Input name: {input_name}')
            try:
                for _ in view_inputs:
                    if not (self.ids[f'input_label_{iterator}'].text).isalpha():
                        n = int(self.ids[f'input_label_{iterator}'].text)
                        function_inputs.append(n)
                        iterator += 1
                    else:
                        function_inputs.append(self.ids[f'input_label_{iterator}'].text)
                        iterator += 1

                function_inputs = tuple(function_inputs)
                print(f'function inputs {function_inputs}')
                if len(view_outputs) == 1:
                    self.ids.output_label_0.text = f'{view_outputs[0].get("name")}: '
                    function_run = eval(f'uploaded_sc.functions.{input_name}(*function_inputs).call()')
                    self.ids.output_label_0.text = f'{self.ids[f"output_label_0"].text} {function_run}'
                else:
                    iterator = 0
                    for _ in view_outputs:
                        self.ids[f"output_label_{iterator}"].text = f'{view_outputs[iterator].get("name")}: '
                        function_run = eval(f'uploaded_sc.functions.{input_name}(*function_inputs).call()[{iterator}]')
                        self.ids[
                            f"output_label_{iterator}"].text = f'{self.ids[f"output_label_{iterator}"].text} {function_run}'
                        iterator += 1
                self.ids.StatusBar_1.text = f'Connected to {contract_address}'

            except web3.exceptions.ValidationError:
                self.ids.StatusBar_1.text = 'Invalid Input'
            except ValueError:
                self.ids.StatusBar_1.text = 'Invalid Input'
        # Nonpayable execution
        elif distinguish == 'nonpayable':
            signed_store_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
            send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
            w3.eth.wait_for_transaction_receipt(send_store_tx)
            self.transaction_count()
            self.update_prices()
            self.ids.calculate_transaction.disabled = True
            self.ids.execute.disabled = True
            self.clear_values()
        # Payable execution
        elif distinguish == 'payable':
            signed_store_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
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
        global abi, contract_abi, network, settings, contract_address, contract_abi, view_mutability, \
            payable_mutability, nonpayable_mutability

        view_mutability = []
        nonpayable_mutability = []
        payable_mutability = []
        contract_abi = ''
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
        global amount_sent, API, ethsc, price, eth_price

        # Network Parameters
        API = settings.get("API")
        ethsc = Etherscan(API, net='main')
        # Get ETH/USD Price
        price = ethsc.get_eth_last_price()
        eth_price = price['ethusd']
        eth_price = round(float(eth_price), 0)

        if self.ids.currency_selection.text == 'Wei':
            pass
        elif self.ids.currency_selection.text == 'Gwei':
            amount_sent = amount_sent * 1000000000
        elif self.ids.currency_selection.text == 'Ethereum':
            amount_sent = amount_sent * 1000000000000000000
        elif self.ids.currency_selection.text == 'USD':
            amount_sent = (amount_sent / eth_price) * 1000000000000000000

        amount_sent = int(amount_sent)

    def transaction_cost_update(self):
        global API, ethsc, price, eth_price, gas_price, gas_price_usd, estimated_gas, w3, gas_cost, upload_cost, \
            upload_cost_usd

        # Network Parameters
        API = settings.get("API")
        ethsc = Etherscan(API, net='main')
        # Get ETH/USD Price
        price = ethsc.get_eth_last_price()
        eth_price = price['ethusd']
        eth_price = round(float(eth_price), 0)

        gas_price_usd = float()
        gas_price = float()

        # Gas Estimation
        estimated_gas = w3.eth.estimateGas(transaction)
        gas_cost = float(w3.eth.gas_price / 1000000000)
        gas_cost = round(float(gas_cost), 3)
        # Gas cost in USD
        gas_price_usd = float(gas_cost) * 0.000000001 * float(eth_price)
        # Transaction cost
        upload_cost = gas_cost * estimated_gas
        upload_cost_usd = (upload_cost / 1000000000) * eth_price
        upload_cost_usd = round(float(upload_cost_usd), 2)
        upload_cost = round(float(upload_cost), 1)
        print(f'Gas price USD: {gas_cost}')
        self.ids.gas_transaction.text = f'{estimated_gas} units'
        self.ids.gas_cost_transaction.text = f'{gas_cost} Gwei'
        self.ids.gas_cost_transaction_usd.text = f"{str('{:f}'.format(gas_price_usd))} USD"
        self.ids.gwei_cost_transaction.text = f'{upload_cost} Gwei'
        self.ids.usd_cost_transaction.text = f'{upload_cost_usd} USD'

    def address_cutting(self):
        global settings, short_address

        short_address = settings.get('Address')
        short_address = short_address[:11]
        short_address = short_address + '...'
        self.ids.address_active.text = short_address
        self.ids.address_active_sc.text = short_address

    def transaction_count(self):
        global settings, estimated_gas, gas_cost, eth_price, data, f, upload_cost_usd, upload_cost

        print(f'ETH price: {eth_price}')
        # Last gas spent
        self.ids.last_gas_spent.text = f'{estimated_gas}'
        self.ids.last_gwei_spent.text = f'{int(upload_cost)}'
        self.ids.last_usd_spent.text = f'{upload_cost_usd}'
        self.ids.last_gas_spent_sc.text = f'{estimated_gas}'
        self.ids.last_gwei_spent_sc.text = f'{int(upload_cost)}'
        self.ids.last_usd_spent_sc.text = f'{upload_cost_usd}'

        # Total gas spent
        print(f'{self.ids.total_gas_used_sc.text} {self.ids.last_gas_spent.text}')
        self.ids.total_gas_used_sc.text = str(eval(f'{self.ids.total_gas_used_sc.text}+{self.ids.last_gas_spent.text}'))
        self.ids.total_gwei_spent_sc.text = str(eval(f'{self.ids.total_gwei_spent_sc.text}+{self.ids.last_gwei_spent.text}'))
        self.ids.total_usd_spent_sc.text = str(eval(f'{self.ids.total_usd_spent_sc.text}+{self.ids.last_usd_spent.text}'))
        self.ids.total_gas_used.text = str(eval(f'{self.ids.total_gas_used.text}+{self.ids.last_gas_spent.text}'))
        self.ids.total_gwei_spent.text = str(eval(f'{self.ids.total_gwei_spent.text}+{self.ids.last_gwei_spent.text}'))
        self.ids.total_usd_spent.text = str(eval(f'{self.ids.total_usd_spent.text}+{self.ids.last_usd_spent.text}'))

        settings.update({'Total Gas used': f'{self.ids.total_gas_used.text}'})
        settings.update({'Total Gwei spent': f'{self.ids.total_gwei_spent.text}'})
        settings.update({' Total USD spent': f'{self.ids.total_usd_spent.text}'})
        print(f'Total gas used: {settings.get("Total Gas used")}')

        with open('settings.json', 'w') as f:
            data = json.dumps(settings, indent=1)
            f.write(data)

    def reset_gas_meter(self):
        global data, f
        # Total gas spent
        self.ids.total_gas_used_sc.text = '0'
        self.ids.total_gwei_spent_sc.text = '0'
        self.ids.total_usd_spent_sc.text = '0'
        self.ids.total_gas_used.text = '0'
        self.ids.total_gwei_spent.text = '0'
        self.ids.total_usd_spent.text = '0'
        # Last gas spent
        self.ids.last_gas_spent.text = '0'
        self.ids.last_gwei_spent.text = '0'
        self.ids.last_usd_spent.text = '0'
        self.ids.last_gas_spent_sc.text = '0'
        self.ids.last_gwei_spent_sc.text = '0'
        self.ids.last_usd_spent_sc.text = '0'

        settings.update({'Total Gas used': f'{self.ids.total_gas_used_sc.text}'})
        settings.update({'Total Gwei spent': f'{self.ids.total_gwei_spent_sc.text}'})
        settings.update({'Total USD spent': f'{self.ids.total_usd_spent.text}'})

        with open('settings.json', 'w') as f:
            data = json.dumps(settings, indent=1)
            f.write(data)

    def test_focus(self, instance):
        if instance:
            print(f'Clicked on {instance}')
        else:
            print(f'Clicked off {instance}')

# #############################################-Class Setup-#############################################
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


class OutputLabel(Label):
    pass


class InputLabel(Label):
    pass


class Input(TextInput):
    pass


class SmartContractOperationsApp(App):
    def build(self):
        Window.clearcolor = (1, 166 / 255, 77 / 255, 1)
        return MyLayout()


if __name__ == '__main__':
    SmartContractOperationsApp().run()
