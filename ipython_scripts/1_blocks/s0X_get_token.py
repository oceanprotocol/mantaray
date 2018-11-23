# %% [markdown]

# <p><center>Ocean Protocol</p>
# <p><center>Trilobite pre-release 0.1</center></p>
# <img src="https://oceanprotocol.com/static/media/logo-white.7b65db16.png" alt="drawing" width="200" align="center"/>
# </center>

# %%
# Ocean Protocol
#
# Trilobite release
#
# <img src="https://oceanprotocol.com/static/media/logo-white.7b65db16.png" alt="drawing" width="200"/>
# <img src="https://oceanprotocol.com/static/media/logo.75e257aa.png" alt="drawing" width="200"/>
#
# %% [markdown]
# # Test functionality of squid-py wrapper.

# %% [markdown]
# <img src="https://3c1703fe8d.site.internapcdn.net/newman/gfx/news/hires/2017/mismatchedey.jpg" alt="drawing" width="200" align="center"/>

# %% [markdown]
# ## Section 1: Import modules, and setup logging

# %% [markdown]
# Imports
#%%
from pathlib import Path
import squid_py.ocean as ocean_wrapper
# from squid_py.utils.web3_helper import convert_to_bytes, convert_to_string, convert_to_text, Web3Helper
import sys
import random
import json
import os
from pprint import pprint
import configparser
# import squid_py.ocean as ocean
from squid_py.ocean.ocean import Ocean
from squid_py.ocean.asset import Asset
import names
import secrets
from squid_py.ddo import DDO
from unittest.mock import Mock
import squid_py
print(squid_py.__version__)
import unittest

# %% [markdown]
# Logging
# %%
import logging
loggers_dict = logging.Logger.manager.loggerDict
logger = logging.getLogger()
logger.handlers = []
# Set level
logger.setLevel(logging.INFO)
FORMAT = "%(levelno)s - %(module)-15s - %(funcName)-15s - %(message)s"
DATE_FMT = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter(FORMAT, DATE_FMT)
# Create handler and assign
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(formatter)
logger.handlers = [handler]
logger.info("Logging started")
# %% [markdown]
# ## Section 2: Instantiate the Ocean Protocol interface

#%%
# The contract addresses are loaded from file
# CHOOSE YOUR CONFIGURATION HERE
PATH_CONFIG = Path.cwd() / 'config_local.ini'
assert PATH_CONFIG.exists(), "{} does not exist".format(PATH_CONFIG)

ocn = Ocean(PATH_CONFIG)
logging.info("Ocean smart contract node connected ".format())

# ocn.config.keeper_path

# %% [markdown]
# ## Section 3: Users and accounts
# %% [markdown]
# List the accounts created in Ganache
#%%

# ocn.accounts is a {address: Account} dict
for address in ocn.accounts:
    acct = ocn.accounts[address]
    print(acct.address)

#%%
# These accounts have a positive ETH balance
for address, account in ocn.accounts.items():
    assert account.balance.eth >= 0
    assert account.balance.ocn >= 0

# %% [markdown]
# Get funds to users
# A simple wrapper for each address is created to represent a user
#
# Users are instantiated and listed

#%%
class User():
    def __init__(self, name, role, address, config_path=None):
        self.name = name
        self.address = address
        self.role = role
        self.locked = True
        self.config_path = config_path

        self.ocn = None
        self.account = None

        # If the account is unlocked, instantiate Ocean and the Account classes
        if self.address.lower() in PASSWORD_MAP:
            password = PASSWORD_MAP[self.address.lower()]

            # The ocean class REQUIRES a .ini file -> need to create this file!
            if not self.config_path:
                self.config_fname = "{}_{}_config.ini".format(self.name,self.role).replace(' ', '_')
                config_path = self.create_config(password) # Create configuration file for this user

            # Instantiate Ocean and Account for this User
            self.ocn = Ocean(config_path)
            self.unlock(password)
            acct_dict_lower = {k.lower(): v for k, v in ocn.accounts.items()}
            self.account = acct_dict_lower[self.address.lower()]

            cleanup=True # Delete this temporary INI
            if cleanup:
                config_path.unlink()


        logging.info(self)

    def unlock(self, password):
        self.ocn._web3.personal.unlockAccount(self.address, password)
        self.locked = False

    def create_config(self,password):
        conf = configparser.ConfigParser()
        conf.read(PATH_CONFIG)
        conf['keeper-contracts']['parity.address'] = self.address
        conf['keeper-contracts']['parity.password'] = password
        out_path = Path.cwd() / 'user_configurations' / self.config_fname
        print(out_path)
        with open(out_path, 'w') as fp:
            conf.write(fp)
        return out_path

    def __str__(self):
        if self.locked:
            status = 'LOCKED'
            return "{:<20} {:<20} LOCKED ACCOUNT".format(self.name, self.role)
        else:
            ocean_token = self.account.ocean_balance
            return "{:<20} {:<20} with {} Ocean token".format(self.name, self.role, ocean_token)

    def __repr__(self):
        return self.__str__()

PASSWORD_MAP = {
    '0x00bd138abd70e2f00903268f3db08f2d25677c9e' : 'node0',
    '0x068ed00cf0441e4829d9784fcbe7b9e26d4bd8d0' : 'secret',
    '0xa99d43d86a0758d5632313b8fa3972b6088a21bb' : 'secret',
}

# # Clean up this dir
# user_config_path = Path.cwd() / 'user_configurations'/'*.ini'
# for f in user_config_path.glob(user_config_path.__str__()):
#     f.unlink()


users = list()
for i, acct_address in enumerate(ocn.accounts):
    if i%2 == 0: role = 'Data Scientist'
    else: role = 'Data Owner'
    user = User(names.get_full_name(), role, acct_address)
    users.append(user)

# Select only unlocked accounts
users = [u for u in users if not u.locked]


#%% [markdown]
# List the users

#%%
for u in users: print(u)

#%% [markdown]
# Get some Ocean token
#%%
for usr in users:
    if usr.account.ocean_balance == 0:
        rcpt = usr.account.request_tokens(random.randint(0,100))
        usr.ocn._web3.eth.waitForTransactionReceipt(rcpt)

#%%
# u1 = users[0]
# u2 = users[1]
# u3 = users[2]
#
# rcpt = u1.ocn.keeper.market.request_tokens(10, u1.address)
# u1.ocn._web3.eth.waitForTransactionReceipt(rcpt)
#
# rcpt = u2.ocn.keeper.market.request_tokens(10, u2.address)
# u2.ocn._web3.eth.waitForTransactionReceipt(rcpt)
#
#
# this_ocn = Ocean(Path.cwd() / 'user_configurations'/ 'Jake_Rutledge_Data_Scientist_config.ini')
# this_ocn.keeper.market.request_tokens(10, '0x068Ed00cF0441e4829D9784fCBe7b9e26D4BD8d0')
# for u in users: print(u)



#%%
"""
# %% [markdown]
# ## Section 4: Find and publish assets
#%%
data_owner = [usr for usr in users if usr.role == 'Data Owner'].pop(0)
print("Data Owner:\n", data_owner)
data_consumer = [usr for usr in users if usr.role == 'Data Scientist'].pop(0)
print("Data Consumer:\n", data_consumer)

#%% [markdown]
# ### 4.1) Metadata - An asset has Metadata, which describes the asset
#%%
path_md = Path(os.path.abspath(__file__)) / '..' / 'catalog/samples/metadata.json'
path_md = path_md.resolve()
assert path_md.exists()
with open(path_md) as f:
    metadata = json.load(f)

# ocn.metadata_store.retire_asset_metadata(asset1.did)

asset_price = 50
service_descriptors = [squid_py.service_agreement.service_factory.ServiceDescriptor.access_service_descriptor(asset_price, '/purchaseEndpoint', '/serviceEndpoint', 600)]
ocn.Client = unittest.mock.Mock({'publish_document': '!encrypted_message!'})
ocn.register_asset(metadata, data_owner.account.address, service_descriptors)

#%% [markdown]
# ### 4.2) DID - An Asset has a single unique identifier (DID)
#%%
did_id = secrets.token_hex(32)
did = squid_py.did.did_generate(did_id)

#%% [markdown]
# ### 4.3) DDO - A DDO is a document which describes the services offered on the Asset
#%%
ddo = squid_py.ddo.DDO(did)

#%% [markdown]
# #### 4.3.1 - Build DDO / private, public keys
#%%
if 0: # DISABLE FOR NOW
    # Add a signature
    private_key = ddo.add_signature()

    # add a proof signed with the private key
    ddo.add_proof(0, private_key)

    # Add the metadata store as a 'service' on the asset
    # The URL of the metadata store is on the Ocean class
    ddo.add_service("Metadata", ocn.metadata_store._base_url, values={ 'metadata': metadata})
    assert ddo.validate()

    # set public key
    public_key_value = squid_py.utils.utilities.get_publickey_from_address(ocn._web3, data_owner.account.address)
    pub_key = squid_py.ddo.public_key_base.PublicKeyBase('keys-1', **{'value': public_key_value, 'owner': data_owner.account.address, 'type': squid_py.ddo.PUBLIC_KEY_STORE_TYPE_HEX})
    pub_key.assign_did(did)
    ddo.add_public_key(pub_key)

    # set authentication
    auth = squid_py.ddo.authentication.Authentication(pub_key, squid_py.ddo.public_key_rsa.PUBLIC_KEY_TYPE_RSA)
    ddo.add_authentication(auth, squid_py.ddo.public_key_rsa.PUBLIC_KEY_TYPE_RSA)

#%% [markdown]
# #### 4.3.2 - Build DDO / Encrypt the content URLs
#%%
if 0:
    assert metadata['base']['contentUrls'], 'contentUrls is required in the metadata base attributes.'
    content_urls_encrypted = self.encrypt_metadata_content_urls(did, json.dumps(metadata['base']['contentUrls']))
    # only assign if the encryption worked
    if content_urls_encrypted:
        metadata['base']['contentUrls'] = content_urls_encrypted

#%% [markdown]
# ### 4.4) Finally, the asset can be instantiated, using our first Data Owner
#%%

this_asset = squid_py.ocean.asset.Asset(ddo,usr.account.address)

print("Asset:\n",this_asset)

# %%
# Load a sample DDO
SAMPLE_DDO_PATH = Path.cwd() / 'sample_assets' / 'ddo_sample_generated_1.json'
assert SAMPLE_DDO_PATH.exists()
with open(SAMPLE_DDO_PATH) as f:
    SAMPLE_DDO_JSON_DICT = json.load(f)

SAMPLE_DDO_JSON_STRING = json.dumps(SAMPLE_DDO_JSON_DICT)

this_ddo = DDO(json_text=SAMPLE_DDO_JSON_STRING)
assert this_ddo.validate()
service = this_ddo.get_service('Metadata')
values = service.get_values()
assert values['metadata']
this_ddo._did

#%% [markdown]
# ### 4.2) Publish - The Metadata Store (Aquarius) holds the DDO
# %%

#%% [markdown]
# OLD
#%%
# The sample asset metadata is stored in a .json file
PATH_ASSET1 = Path.cwd() / 'sample_assets' / 'sample1.json'
assert PATH_ASSET1.exists()
with open(PATH_ASSET1) as f:
    dataset = json.load(f)

logging.info("Asset metadata for {}: type={}, price={}".format(dataset['base']['name'],dataset['base']['type'],dataset['base']['price']))

registered_asset = users[0].register_asset(dataset)

asset = ocn.metadata.register_asset(dataset)
assert ocean_provider.metadata.get_asset_ddo(asset['assetId'])['base']['name'] == asset['base']['name']
ocean_provider.metadata.retire_asset(asset['assetId'])

# %% List assets
asset_ddo = ocn.metadata.get_asset_ddo(dataset['assetId'])
assert ocn.metadata.get_asset_ddo(dataset['assetId'])['base']['name'] == dataset['base']['name']


"""
