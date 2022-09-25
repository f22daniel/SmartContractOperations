import json


class Settings:

    def __init__(self, json_path):
        try:
            with open(json_path, 'r') as f:
                data = json.loads(f.read())
        except FileNotFoundError:
            raise ValueError("JSON not found")

        self.address = data.get('Address')
        self.private_key = data.get('Private Key')
        self.etherscan_api = data.get('API')
        self.infura_api = data.get('Infura')
        self.bsc_api = data.get('BSC API')
        self.ganache_address = data.get('Ganache Address')
        self.ganache_private_key = data.get('Ganache Private Key')
        self.gas_limit = data.get('Gas Limit')
        self.ganache_id = data.get('Ganache ID')
        self.infura_link = data.get('Infura Link')
        self.network = data.get('Network')
        self.solidity_compiler = data.get('Solidity Compiler')
        self.last_contract = data.get('Last Contract')
        self.ganache_rpc = data.get('Ganache RPC')
        self.chain_id = data.get('Chain ID')
        self.full_compiler = data.get('Full Compiler')

        self.address_1 = data['Addresses']['Address 1']
        self.address_2 = data['Addresses']['Address 2']
        self.address_3 = data['Addresses']['Address 3']
        self.address_4 = data['Addresses']['Address 4']
        self.address_5 = data['Addresses']['Address 5']
        self.address_6 = data['Addresses']['Address 6']
        self.addresses = data.get('Addresses')
        self.private_keys = data.get('Private Keys')
        self.private_key_1 = data['Private Keys']['Private Key 1']
        self.private_key_2 = data['Private Keys']['Private Key 2']
        self.private_key_3 = data['Private Keys']['Private Key 3']
        self.private_key_4 = data['Private Keys']['Private Key 4']
        self.private_key_5 = data['Private Keys']['Private Key 5']
        self.private_key_6 = data['Private Keys']['Private Key 6']
        self.total_gas_used = data.get('Total Gas used')
        self.total_gwei_spent = data.get('Total Gwei spent')
        self.total_usd_spent = data.get('Total USD spent')
        self.contract_web_page = data.get('Contract Web Page')

    def update_json(self, json_path='/Users/f22daniel/PycharmProjects/Griraffe/smart_contract_development/Kivy_App/settings.json'):
        data = {'Address': self.address, 'Private Key': self.private_key, 'API': self.etherscan_api, 'BSC API': self.bsc_api,
                'Infura': self.infura_api, 'Gas Limit': self.gas_limit, 'Ganache Address': self.ganache_address,
                'Ganache ID': self.ganache_id, 'Infura Link': self.infura_link, 'Network': self.network, 'Contract Web Page': self.contract_web_page,
                'Solidity Compiler': self.solidity_compiler, 'Last Contract': self.last_contract, 'Ganache RPC': self.ganache_rpc,
                'Ganache Private Key': self.ganache_private_key, 'Chain ID': self.chain_id, 'Full Compiler': self.full_compiler,
                'Addresses': {'Address 1': self.address_1, 'Address 2': self.address_2, 'Address 3': self.address_3,
                'Address 4': self.address_4,'Address 5': self.address_5, 'Address 6': self.address_6}, 'Private Keys': {
                'Private Key 1': self.private_key_1, 'Private Key 2': self.private_key_2, 'Private Key 3': self.private_key_3,
                'Private Key 4': self.private_key_4, 'Private Key 5': self.private_key_5, 'Private Key 6': self.private_key_6},
                'Total Gas used': self.total_gas_used, 'Total Gwei spent': self.total_gwei_spent, 'Total USD spent': self.total_usd_spent}

        with open(json_path, 'w') as f:
            data = json.dumps(data, indent=1)
            f.write(data)


class Variables:

    def __init__(self, abi='', my_address='', bytecode='', ethsc=None, price=None, eth_price=None, gas=None, gas_price=None,
                 contract_address='', compiled_contract='', constructor_inputs=None, w3='', transaction='', uploaded_sc='',
                 contract_abi='', view_mutability=None, payable_mutability=None, nonpayable_mutability=None, gas_price_wei=None,
                 input_name='', view_outputs='', view_inputs='', nonpayable_inputs='', payable_inputs='', upload_cost_usd='',
                 distinguish='', function_name='', nonce='', amount_sent=float(), estimated_gas='', gas_cost='', subcontract='',
                 gas_price_usd=None, balance=None, conf_time=None, sc_file_path='', sc_file_name='', sc_file_keys=None, ):
        if sc_file_keys is None:
            sc_file_keys = []
        if nonpayable_mutability is None:
            nonpayable_mutability = []
        if payable_mutability is None:
            payable_mutability = []
        if view_mutability is None:
            view_mutability = []
        if constructor_inputs is None:
            constructor_inputs = []

        self.abi = abi
        self.my_address = my_address
        self.bytecode = bytecode
        self.contract_address = contract_address
        self.compiled_contract = compiled_contract
        self.constructor_inputs = constructor_inputs
        self.nonpayable_mutability = nonpayable_mutability
        self.payable_mutability = payable_mutability
        self.view_mutability = view_mutability
        self.w3 = w3
        self.transaction = transaction
        self.uploaded_sc = uploaded_sc
        self.contract_abi = contract_abi
        self.input_name = input_name
        self.view_outputs = view_outputs
        self.view_inputs = view_inputs
        self.nonpayable_inputs = nonpayable_inputs
        self.payable_inputs = payable_inputs
        self.distinguish = distinguish
        self.function_name = function_name
        self.nonce = nonce
        self.amount_sent = amount_sent
        self.estimated_gas = estimated_gas
        self.gas_cost = gas_cost
        self.upload_cost_usd = upload_cost_usd
        self.ethsc = ethsc
        self.gas_price_usd = gas_price_usd
        self.price = price
        self.eth_price = eth_price
        self.gas = gas
        self.gas_price = gas_price
        self.gas_price_wei = gas_price_wei
        self.balance = balance
        self.conf_time = conf_time
        self.sc_file_path = sc_file_path
        self.sc_file_name = sc_file_name
        self.sc_file_keys = sc_file_keys
        self.subcontract = subcontract


settings_test = Settings("/Users/f22daniel/PycharmProjects/Griraffe/smart_contract_development/Kivy_App/settings.json")
variables_test = Variables()

'''
for x in range(1, 7):
    print(settings_test.addresses[f'Address {x}'])

for x in range(1, 7):
    print(settings_test.private_keys[f'Private Key {x}'])
'''