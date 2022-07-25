import binascii

import requests.exceptions
import solcx.exceptions
import web3
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.button import Button
from kivy.graphics import *
from kivy.uix.tabbedpanel import *
from functools import partial
# import time
# from kivy.clock import Clock
import json
from etherscan import Etherscan
from kivy.uix.textinput import TextInput
from plyer import filechooser
from solcx import compile_standard, install_solc
from web3 import Web3
from web3 import exceptions
import ast

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

Builder.load_file('SC_App.kv')
Window.size = (1100, 600)
settings = {'Address': '', 'Private Key': '', 'API': '', 'Infura': '', 'Gas Limit': '', 'Ganache Address': '',
            'Ganache ID': '', 'Mainnet': '', 'Goerli': '', 'Kovan': '', 'Rinkeby': '', 'Ropsten': '', 'Ganache': '',
            'Infura Link': '', 'Currency': '', 'Network': '', 'Solidity Compiler': '', 'Chain ID': '',
            'Last Contract': '', 'Ganache RPC': '', 'Ganache Private Key': ''}

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
            # Network Parameters
            API = settings.get("API")
            network = settings.get('Network')
            ethsc = Etherscan(API, net='main')
            # Get ETH/USD Price
            price = ethsc.get_eth_last_price()
            eth_price = price['ethusd']
            eth_price = round(float(eth_price), 0)
            self.ids.ETH_Price.text = f'{int(eth_price)} USD'
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
            else:
                ethsc = Etherscan(API, net=(settings.get('Network')))
                balance = ethsc.get_eth_balance(f'{settings.get("Address")}')
                balance = f'{str(eval(f"{balance}*0.000000000000000001"))}'
                balance = round(float(balance), 4)
                self.ids.Wallet_Balance.text = str(f'{balance} ETH')
                print(self.ids.Wallet_Balance.text)
            print('Checkpoint')
            # Network Selection
            if settings['Mainnet'] == 'down':
                self.ids.Mainnet.state = 'down'
                self.ids.active_network.text = 'Mainnet'
                settings.update({'Network': 'main'})
                settings.update({'Infura Link': f'https://mainnet.infura.io/v3/{settings.get("Infura")}'})
                w3 = Web3.HTTPProvider(settings.get('Infura Link'))
                settings.update({'Chain ID': 1})
                chain_id = settings.get('Chain ID')
            if settings['Goerli'] == 'down':
                self.ids.Goerli.state = 'down'
                self.ids.active_network.text = 'Goerli'
                settings.update({'Network': 'goerli'})
                settings.update({'Infura Link': f'https://goerli.infura.io/v3/{settings.get("Infura")}'})
                w3 = Web3.HTTPProvider(settings.get('Infura Link'))
                settings.update({'Chain ID': 5})
                chain_id = settings.get('Chain ID')
            if settings['Kovan'] == 'down':
                self.ids.Kovan.state = 'down'
                self.ids.active_network.text = 'Kovan'
                settings.update({'Network': 'kovan'})
                settings.update({'Infura Link': f'https://kovan.infura.io/v3/{settings.get("Infura")}'})
                w3 = Web3.HTTPProvider(settings.get('Infura Link'))
                settings.update({'Chain ID': 42})
                chain_id = settings.get('Chain ID')
            if settings['Rinkeby'] == 'down':
                self.ids.Rinkeby.state = 'down'
                self.ids.active_network.text = 'Rinkeby'
                settings.update({'Network': 'rinkeby'})
                settings.update({'Infura Link': f'https://rinkeby.infura.io/v3/{settings.get("Infura")}'})
                w3 = Web3.HTTPProvider(settings.get('Infura Link'))
                settings.update({'Chain ID': 4})
                chain_id = settings.get('Chain ID')
            if settings['Ropsten'] == 'down':
                self.ids.Ropsten.state = 'down'
                self.ids.active_network.text = 'Ropsten'
                settings.update({'Network': 'ropsten'})
                settings.update({'Infura Link': f'https://ropsten.infura.io/v3/{settings.get("Infura")}'})
                w3 = Web3.HTTPProvider(settings.get('Infura Link'))
                settings.update({'Chain ID': 3})
                chain_id = settings.get('Chain ID')
            if settings['Ganache'] == 'down':
                self.ids.Ganache.state = 'down'
                self.ids.active_network.text = 'Ganache'
                settings.update({'Network': 'ganache'})
        except AssertionError as e:
            self.ids.StatusBar.text = str(e)
        except ValueError as e:
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
        # Install solidity compiler
        install_solc(f'{self.ids.SolidityCompiler.text}')

    # ################################################-Tab 3-################################################
    # Settings Confirmation
    def address_enter(self):
        global data, f
        settings.update({'Address': f'{self.ids.AddressEnter.text}'})
        self.ids.AddressEnter.text = self.ids.AddressEnter.text.strip()
        with open('settings.json', 'w') as f:
            data = json.dumps(settings, indent=1)
            f.write(data)

    def private_key_enter(self):
        global data, f
        settings.update({'Private Key': f'{self.ids.PrivateKeyEnter.text}'})
        self.ids.PrivateKeyEnter.text = self.ids.PrivateKeyEnter.text.strip()
        with open('settings.json', 'w') as f:
            data = json.dumps(settings, indent=1)
            f.write(data)

    def api_enter(self):
        global data, f, API, network, ethsc
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

    def infura_enter(self):
        global data, f, w3
        settings.update({'Infura': f'{self.ids.InfuraEnter.text}'})
        self.ids.InfuraEnter.text = self.ids.InfuraEnter.text.strip()
        infura_network = str.lower(self.ids.active_network.text)
        settings.update({'Infura Link': f'https://{infura_network}.infura.io/v3/{self.ids.InfuraEnter.text}'})
        w3 = Web3.HTTPProvider(settings.get('Infura Link'))
        with open('settings.json', 'w') as f:
            data = json.dumps(settings, indent=1)
            f.write(data)

    def gas_enter(self):
        global data, f
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

    def ganache_rpc_enter(self):
        global data, f
        settings.update({'Ganache RPC': f'{self.ids.GanacheRPCEnter.text}'})
        self.ids.GanacheRPCEnter.text = self.ids.GanacheRPCEnter.text.strip()
        with open('settings.json', 'w') as f:
            data = json.dumps(settings, indent=1)
            f.write(data)

    def ganache_id_enter(self):
        global data, f
        text = self.ids.GanacheIDEnter.text
        try:
            int(text)
            settings.update({'Ganache ID': f'{self.ids.GanacheIDEnter.text}'})
            with open('settings.json', 'w') as f:
                data = json.dumps(settings, indent=1)
                f.write(data)
        except ValueError:
            self.ids.GanacheIDEnter.text = 'Error'

    def solidity_compiler_enter(self):
        global data, f
        settings.update({'Solidity Compiler': f'{self.ids.SolidityCompiler.text}'})
        self.ids.SolidityCompiler.text = self.ids.SolidityCompiler.text.strip()
        install_solc(f'{self.ids.SolidityCompiler.text}')
        with open('settings.json', 'w') as f:
            data = json.dumps(settings, indent=1)
            f.write(data)

    def ganache_address_enter(self):
        global data, f
        print('Confirm')
        settings.update({'Ganache Address': f'{self.ids.GanacheAddressEnter.text}'})
        self.ids.GanacheAddressEnter.text = self.ids.GanacheAddressEnter.text.strip()
        with open('settings.json', 'w') as f:
            data = json.dumps(settings, indent=1)
            f.write(data)

    def ganache_private_key_enter(self):
        global data, f
        settings.update({'Ganache Private Key': f'{self.ids.GanachePrivateKeyEnter.text}'})
        self.ids.GanachePrivateKeyEnter.text = self.ids.GanachePrivateKeyEnter.text.strip()
        with open('settings.json', 'w') as f:
            data = json.dumps(settings, indent=1)
            f.write(data)

    # Network selection
    def mainnet_network(self):
        global data, f, network, ethsc, w3, chain_id, balance
        try:
            if self.ids.Mainnet.state == 'down':
                settings.update({'Mainnet': 'down'})
                self.ids.Goerli.state = 'normal'
                settings.update({'Goerli': 'normal'})
                self.ids.Kovan.state = 'normal'
                settings.update({'Kovan': 'normal'})
                self.ids.Rinkeby.state = 'normal'
                settings.update({'Rinkeby': 'normal'})
                self.ids.Ropsten.state = 'normal'
                settings.update({'Ropsten': 'normal'})
                self.ids.Ganache.state = 'normal'
                settings.update({'Ganache': 'normal'})
                self.ids.active_network.text = 'Mainnet'
                settings.update({'Infura Link': f'https://mainnet.infura.io/v3/{settings.get("Infura")}'})
                settings.update({'Network': 'main'})
                network = settings.get("Network")
                ethsc = Etherscan(API, net=network)
                w3 = Web3.HTTPProvider(settings.get('Infura Link'))
                settings.update({'Chain ID': 1})
                chain_id = settings.get('Chain ID')
                ethsc = Etherscan(API, net=(settings.get('Network')))
                balance = ethsc.get_eth_balance(f'{settings.get("Address")}')
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
        global data, f, network, ethsc, w3, chain_id, balance
        try:
            if self.ids.Goerli.state == 'down':
                settings.update({'Goerli': 'down'})
                self.ids.Mainnet.state = 'normal'
                settings.update({'Mainnet': 'normal'})
                self.ids.Kovan.state = 'normal'
                settings.update({'Kovan': 'normal'})
                self.ids.Rinkeby.state = 'normal'
                settings.update({'Rinkeby': 'normal'})
                self.ids.Ropsten.state = 'normal'
                settings.update({'Ropsten': 'normal'})
                self.ids.Ganache.state = 'normal'
                settings.update({'Ganache': 'normal'})
                self.ids.active_network.text = 'Goerli'
                settings.update({'Infura Link': f'https://goerli.infura.io/v3/{settings.get("Infura")}'})
                settings.update({'Network': 'goerli'})
                network = settings.get("Network")
                ethsc = Etherscan(API, net=network)
                w3 = Web3.HTTPProvider(settings.get('Infura Link'))
                settings.update({'Chain ID': 5})
                chain_id = settings.get('Chain ID')
                ethsc = Etherscan(API, net=(settings.get('Network')))
                balance = ethsc.get_eth_balance(f'{settings.get("Address")}')
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
        global data, f, network, ethsc, w3, chain_id, balance
        try:
            if self.ids.Kovan.state == 'down':
                settings.update({'Kovan': 'down'})
                self.ids.Mainnet.state = 'normal'
                settings.update({'Mainnet': 'normal'})
                self.ids.Goerli.state = 'normal'
                settings.update({'Goerli': 'normal'})
                self.ids.Rinkeby.state = 'normal'
                settings.update({'Rinkeby': 'normal'})
                self.ids.Ropsten.state = 'normal'
                settings.update({'Ropsten': 'normal'})
                self.ids.Ganache.state = 'normal'
                settings.update({'Ganache': 'normal'})
                self.ids.active_network.text = 'Kovan'
                settings.update({'Infura Link': f'https://kovan.infura.io/v3/{settings.get("Infura")}'})
                settings.update({'Network': 'kovan'})
                network = settings.get("Network")
                ethsc = Etherscan(API, net=network)
                w3 = Web3.HTTPProvider(settings.get('Infura Link'))
                settings.update({'Chain ID': 42})
                chain_id = settings.get('Chain ID')
                ethsc = Etherscan(API, net=(settings.get('Network')))
                balance = ethsc.get_eth_balance(f'{settings.get("Address")}')
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
        global data, f, network, ethsc, w3, chain_id, balance
        try:
            if self.ids.Rinkeby.state == 'down':
                settings.update({'Rinkeby': 'down'})
                self.ids.Mainnet.state = 'normal'
                settings.update({'Mainnet': 'normal'})
                self.ids.Kovan.state = 'normal'
                settings.update({'Kovan': 'normal'})
                self.ids.Goerli.state = 'normal'
                settings.update({'Goerli': 'normal'})
                self.ids.Ropsten.state = 'normal'
                settings.update({'Ropsten': 'normal'})
                self.ids.Ganache.state = 'normal'
                settings.update({'Ganache': 'normal'})
                self.ids.active_network.text = 'Rinkeby'
                settings.update({'Infura Link': f'https://rinkeby.infura.io/v3/{settings.get("Infura")}'})
                settings.update({'Network': 'rinkeby'})
                network = settings.get("Network")
                ethsc = Etherscan(API, net=network)
                w3 = Web3.HTTPProvider(settings.get('Infura Link'))
                settings.update({'Chain ID': 4})
                chain_id = settings.get('Chain ID')
                ethsc = Etherscan(API, net=(settings.get('Network')))
                balance = ethsc.get_eth_balance(f'{settings.get("Address")}')
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
        global data, f, network, ethsc, w3, chain_id, balance
        try:
            if self.ids.Ropsten.state == 'down':
                settings.update({'Ropsten': 'down'})
                self.ids.Mainnet.state = 'normal'
                settings.update({'Mainnet': 'normal'})
                self.ids.Kovan.state = 'normal'
                settings.update({'Kovan': 'normal'})
                self.ids.Rinkeby.state = 'normal'
                settings.update({'Rinkeby': 'normal'})
                self.ids.Ganache.state = 'normal'
                settings.update({'Ganache': 'normal'})
                self.ids.active_network.text = 'Ropsten'
                settings.update({'Infura Link': f'https://ropsten.infura.io/v3/{settings.get("Infura")}'})
                settings.update({'Network': 'ropsten'})
                network = settings.get("Network")
                ethsc = Etherscan(API, net=network)
                w3 = Web3.HTTPProvider(settings.get('Infura Link'))
                settings.update({'Chain ID': 3})
                chain_id = settings.get('Chain ID')
                ethsc = Etherscan(API, net=(settings.get('Network')))
                balance = ethsc.get_eth_balance(f'{settings.get("Address")}')
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
        global data, f, w3
        try:
            if self.ids.Ganache.state == 'down':
                settings.update({'Ganache': 'down'})
                self.ids.Mainnet.state = 'normal'
                settings.update({'Mainnet': 'normal'})
                self.ids.Kovan.state = 'normal'
                settings.update({'Kovan': 'normal'})
                self.ids.Rinkeby.state = 'normal'
                settings.update({'Rinkeby': 'normal'})
                self.ids.Ropsten.state = 'normal'
                settings.update({'Ropsten': 'normal'})
                self.ids.Goerli.state = 'normal'
                settings.update({'Goerli': 'normal'})
                self.ids.active_network.text = 'Ganache'
                settings.update({'Network': 'ganache'})
                w3 = Web3(Web3.HTTPProvider(settings.get('Ganache RPC')))
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
            # w3 declaration
            if settings.get('Network') != 'ganache':
                infura = settings.get('Infura Link')
                w3 = Web3(Web3.HTTPProvider(infura))
            else:
                w3 = Web3(Web3.HTTPProvider(settings.get('Ganache RPC')))
            # ETH Price update
            ethsc = Etherscan(API, net='main')
            price = ethsc.get_eth_last_price()
            eth_price = price['ethusd']
            eth_price = round(float(eth_price), 0)
            self.ids.ETH_Price.text = f'{int(eth_price)} USD'
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
            else:
                ethsc = Etherscan(API, net=(settings.get('Network')))
                balance = ethsc.get_eth_balance(f'{settings.get("Address")}')
                balance = f'{str(eval(f"{balance}*0.000000000000000001"))}'
                balance = round(float(balance), 4)
                self.ids.Wallet_Balance.text = str(f'{balance} ETH')
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
            self.ids.StatusBar.text = 'Wrong compiler set. Please check Settings or Contract'
            # solc_error = str(e)
            # print(f'{solc_error}')
        except AttributeError:
            pass

    def select_subcontract(self, text, *args):
        global sc_file_path, compiled_contract, sc_file_name, bytecode, sc_file_keys, abi, constructor_inputs, \
            subcontract_name

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
        global abi, bytecode, chain_id, constructor_inputs, w3, price, eth_price, ethsc, API, transaction, infura

        try:
            constructor_count = 0
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
                    constructor_inputs[constructor_count] = self.ids[f'ConstructorInput_{constructor_count}'].text
                    constructor_count += 1
                # else:
                #     constructor_inputs[constructor_count] = self.ids[f'ConstructorInput_{constructor_count}'].text
                #     constructor_count += 1
            print(f'Type {type(w3)}')
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
            settings.update({'Last Contract': f'{contract_address}'})
            # Wallet Balance update
            if settings.get('Network') == 'ganache':
                w3_balance = w3.eth.getBalance(settings.get('Ganache Address'))
                w3_balance = f'{str(eval(f"{w3_balance}*0.000000000000000001"))}'
                w3_balance = round(float(w3_balance), 4)
                self.ids.Wallet_Balance.text = str(f'{w3_balance} ETH')
            else:
                ethsc = Etherscan(API, net=(settings.get('Network')))
                balance = ethsc.get_eth_balance(f'{settings.get("Address")}')
                balance = f'{str(eval(f"{balance}*0.000000000000000001"))}'
                balance = round(float(balance), 4)
                self.ids.Wallet_Balance.text = str(f'{balance} ETH')
                print(self.ids.Wallet_Balance.text)
            # Update JSON
            with open('settings.json', 'w') as f:
                data = json.dumps(settings, indent=1)
                f.write(data)
            # Enable/Disable Buttons
            self.ids.DeploySC.disabled = True
        except binascii.Error as e:
            self.ids.StatusBar.text = str(e)
        except ValueError as e:
            self.ids.StatusBar.text = str(e)

    # ################################################-Tab 1-################################################
    def activate_uploaded_sc(self):
        global settings, ethsc, API, network, contract_address, contract_abi, iterator, x, view_mutability, \
            nonpayable_mutability, payable_mutability, infura, w3

        iterator = 0
        view_mutability = []
        nonpayable_mutability = []
        payable_mutability = []

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
            self.ids.grid_id_3.add_widget(view_button)
            view_button.bind(on_release=partial(self.view_function_execution, view_button.text))
            iterator += 1

        iterator = 0

        for _ in nonpayable_mutability:
            print((nonpayable_mutability[iterator]).get('name'))
            nonpayable_button = NonepayableButton(text=(nonpayable_mutability[iterator]).get('name'))
            self.ids[f'{(nonpayable_mutability[iterator]).get("name")}'] = nonpayable_button
            self.ids.grid_id_2.add_widget(nonpayable_button)
            nonpayable_button.bind(on_release=partial(self.nonpayable_function_execution, nonpayable_button.text))
            iterator += 1

        iterator = 0

        for _ in payable_mutability:
            print((payable_mutability[iterator]).get('name'))
            payable_button = PayableButton(text=(payable_mutability[iterator]).get('name'))
            self.ids[f'{(payable_mutability[iterator]).get("name")}'] = payable_button
            self.ids.grid_id_1.add_widget(payable_button)
            payable_button.bind(on_release=partial(self.payable_function_execution, payable_button.text))
            iterator += 1

        self.ids.UploadedSC.disabled = True
        self.ids.ExternalSC.disabled = True

    def connect_to_sc(self):
        global ethsc, API, network, function, variable, view_mutability, payable_mutability, uploaded_sc, \
            nonpayable_mutability, API, network, settings, contract_address, contract_abi, iterator, x, w3, infura

        iterator = 0
        view_mutability = []
        nonpayable_mutability = []
        payable_mutability = []

        # w3 declaration
        if settings.get('Network') != 'ganache':
            infura = settings.get('Infura Link')
            w3 = Web3(Web3.HTTPProvider(infura))
        else:
            w3 = Web3(Web3.HTTPProvider(settings.get('Ganache RPC')))

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
            self.ids.grid_id_3.add_widget(view_button)
            view_button.bind(on_release=partial(self.view_function_execution, view_button.text))
            iterator += 1

        iterator = 0

        for _ in nonpayable_mutability:
            print((nonpayable_mutability[iterator]).get('name'))
            nonpayable_button = NonepayableButton(text=(nonpayable_mutability[iterator]).get('name'))
            self.ids[f'{(nonpayable_mutability[iterator]).get("name")}'] = nonpayable_button
            self.ids.grid_id_2.add_widget(nonpayable_button)
            nonpayable_button.bind(on_release=partial(self.nonpayable_function_execution, nonpayable_button.text))
            iterator += 1

        iterator = 0

        for _ in payable_mutability:
            print((payable_mutability[iterator]).get('name'))
            payable_button = PayableButton(text=(payable_mutability[iterator]).get('name'))
            self.ids[f'{(payable_mutability[iterator]).get("name")}'] = payable_button
            self.ids.grid_id_1.add_widget(payable_button)
            payable_button.bind(on_release=partial(self.payable_function_execution, payable_button.text))
            iterator += 1

        self.ids.UploadedSC.disabled = True
        self.ids.ExternalSC.disabled = True

        # view functions

    def view_function_execution(self, text, *args):
        global iterator, view_mutability

        view_function = ''
        input_name = ''
        iterator = 0
        self.ids.output_layout.clear_widgets()
        self.ids.input_layout.clear_widgets()

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
            self.ids.output_layout.add_widget(output_label)
            iterator += 1
        # Input widgets
        iterator = 0
        view_inputs = view_function.get('inputs')
        print(view_inputs)
        if len(view_inputs) != 0:
            for _ in view_inputs:
                print(view_inputs[iterator].get('name'))
                input_label = InputLabel(text=f'{view_inputs[iterator].get("name")}:')
                input_text = Input(text=f'{view_inputs[iterator].get("type")}')
                self.ids[f'input_label_{iterator}'] = input_text
                # Add widgets
                self.ids.input_layout.add_widget(input_label)
                self.ids.input_layout.add_widget(input_text)
                # Enable execute button
                self.ids.execute.disabled = False
                iterator += 1
        else:
            self.ids.execute.disabled = True
            function_run = eval(f'')

        # Nonpayable functions
    def nonpayable_function_execution(self, text, *args):
        global iterator

        iterator = 0
        nonpayable_function = ''

        self.ids.output_layout.clear_widgets()
        self.ids.input_layout.clear_widgets()

        for _ in nonpayable_mutability:
            if text == nonpayable_mutability[iterator].get('name'):
                nonpayable_function = nonpayable_mutability[iterator]
                print(nonpayable_function)
                break
            iterator += 1
        # Output widgets
        iterator = 0
        nonpayable_outputs = nonpayable_function.get('outputs')
        if len(nonpayable_outputs) != 0:
            for _ in nonpayable_outputs:
                print(nonpayable_outputs[iterator].get('name'))
                output_label = OutputLabel(text=f'{nonpayable_outputs[iterator].get("name")}: ')
                self.ids.output_layout.add_widget(output_label)
                iterator += 1
        else:
            pass
        # Input widgets
        iterator = 0
        nonpayable_inputs = nonpayable_function.get('inputs')
        print(nonpayable_inputs)
        if len(nonpayable_inputs) != 0:
            for _ in nonpayable_inputs:
                print(nonpayable_inputs[iterator].get('name'))
                input_label = InputLabel(text=f'{nonpayable_inputs[iterator].get("name")}:')
                input_text = Input(text=f'{nonpayable_inputs[iterator].get("type")}')
                self.ids[f'input_label_{iterator}'] = input_text
                # Add widgets
                self.ids.input_layout.add_widget(input_label)
                self.ids.input_layout.add_widget(input_text)
                # Enable execute button
                self.ids.execute.disabled = False
                iterator += 1
        else:
            self.ids.execute.disabled = True

        # Payable function
    def payable_function_execution(self, text, *args):
        global iterator

        iterator = 0
        payable_function = ''

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
        nonpayable_inputs = payable_function.get('inputs')
        print(nonpayable_inputs)
        if len(nonpayable_inputs) != 0:
            for _ in nonpayable_inputs:
                print(nonpayable_inputs[iterator].get('name'))
                input_label = InputLabel(text=f'{nonpayable_inputs[iterator].get("name")}:')
                input_text = Input(text=f'{nonpayable_inputs[iterator].get("type")}')
                self.ids[f'input_label_{iterator}'] = input_text
                # Add widgets
                self.ids.input_layout.add_widget(input_label)
                self.ids.input_layout.add_widget(input_text)
                # Enable execute button
                self.ids.execute.disabled = False
                iterator += 1
        else:
            self.ids.execute.disabled = True

    def execute_inputs(self):
        global iterator
        iterator = 0
        print('Button pressed')
        # print(f'Input name: {input_name}')
        try:
            print(self.ids.input_label_0.text)
            print(self.ids.input_label_1.text)
            print(self.ids.input_label_2.text)
        except AttributeError:
            pass

    def clear_sc_address(self):
        global abi, contract_abi, network, settings, contract_address, contract_abi, view_mutability, \
            payable_mutability, nonpayable_mutability

        view_mutability = []
        nonpayable_mutability = []
        payable_mutability = []
        contract_abi = ''
        self.ids.ContractAddress.text = ''
        self.ids.grid_id_1.clear_widgets()
        self.ids.grid_id_2.clear_widgets()
        self.ids.grid_id_3.clear_widgets()
        self.ids.input_layout.clear_widgets()
        self.ids.output_layout.clear_widgets()
        self.ids.StatusBar_1.text = 'Connect to SC'
        self.ids.UploadedSC.disabled = False
        self.ids.ExternalSC.disabled = False


# #############################################-Class Setup-#############################################
class ConstructorLabel(Label):
    def on_size(self, *args):
        self.canvas.before.clear()
        self.size_hint = (1, 1)
        with self.canvas.before:
            Color(179 / 255, 89 / 255, 0, 1)
            Rectangle(pos=self.pos, size=self.size)


class SubcontractToggle(ToggleButton):
    def on_size(self, *args):
        self.canvas.before.clear()
        self.size_hint = (1, 1)
        self.background_normal = ''
        self.background_color = (128 / 255, 77 / 255, 0, 1)
        self.bold = True
        self.font_size = 16


class ConstructorText(TextInput):
    def on_size(self, *args):
        self.multiline = False
        self.size_hint = (1, 1)


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
