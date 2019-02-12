# %% [markdown]
# # Getting Underway - Publishing assets
# In this notebook, we will explore how to publish an Asset using Ocean Protocol.
# As described in the previous notebook, Publish consists of 2 aspects:
#
# 1. Uploading the DDO to Aquarius
# 1. Registering the Asset on the blockchain
#
# *Note to the reader! The current implementation is very low-level, most of the functionality will be wrapped into
# simpler Ocean.publish_dataset() style methods!*
# %% [markdown]
# ### Section 0: Import modules, and setup logging

#%%
# Standard imports
import logging
# from pathlib import Path
import os

# Import mantaray and the Ocean API (squid)
import random
import squid_py
from squid_py.ocean.ocean import Ocean
from squid_py.config import Config
import mantaray_utilities as manta_utils
from mantaray_utilities.user import password_map
from pprint import pprint
# Setup logging
manta_utils.logging.logger.setLevel('CRITICAL')
# os.environ['USE_K8S_CLUSTER'] = 'True' # Enable this for testing local -> AWS setup
#%%
# Get the configuration file path for this environment
# os.environ['USE_K8S_CLUSTER'] = 'true'
CONFIG_INI_PATH = manta_utils.config.get_config_file_path()
logging.critical("Deployment type: {}".format(manta_utils.config.get_deployment_type()))
logging.critical("Configuration file selected: {}".format(CONFIG_INI_PATH))
logging.critical("Squid API version: {}".format(squid_py.__version__))

# %% [markdown]
# ### Section 1: A publisher account in Ocean
#
#%%
# Instantiate Ocean with the default configuration file.
configuration = Config(CONFIG_INI_PATH)
ocn = Ocean(configuration)
#%%
# Get a publisher account
path_passwords = manta_utils.config.get_project_path() / 'passwords.csv'
passwords = manta_utils.user.load_passwords(path_passwords)

publisher_acct = random.choice([acct for acct in ocn.accounts.list() if password_map(acct.address, passwords)])
publisher_acct.password = password_map(publisher_acct.address, passwords)
assert publisher_acct.password
#%%
print("Publisher account:", publisher_acct.address, publisher_acct.password)
# publisher_address = configuration['keeper-contracts']['parity.address']
# publisher_pass = configuration['keeper-contracts']['parity.password']
# publisher_acct = [ocn.accounts[addr] for addr in ocn.accounts if addr.lower() == publisher_address.lower()][0]
# publisher_acct.password = publisher_pass

# %% [markdown]
# Your account will need some Ocean Token to make real transactions
# %%
# ensure Ocean token balance
if publisher_acct.ocean_balance == 0:
    tx_hash = publisher_acct.request_tokens(1)
    Web3Provider.get_web3().eth.waitForTransactionReceipt(tx_hash)
#%% [markdown]
# For this tutorial, we will select one of the available unlocked accounts.
#
# In general, as a publisher, you will have your own configuration file with your personal account.

#%% [markdown]
# ### Section 2: Create your MetaData for your asset
# A more complex use case is to manually generate your metadata conforming to Ocean standard, but for demonstration purposes,
# a utility in squid-py is used to generate a sample Meta Data dictionary.

#%%
# Get a simple example of Meta Data from the library directly
metadata = squid_py.ddo.metadata.Metadata.get_example()
print('Name of asset:', metadata['base']['name'])

pprint(metadata)


# %% [markdown]
# Note the price in the Metadata! This will be purchase price you are placing on the asset.
#
# The asset has been constructed, we are ready to publish to Ocean Protocol!
# %%
ddo = ocn.register_asset(metadata, publisher_acct)

# %%
# Inspect the new DDO
registered_did = ddo.did
print("New asset registered at", registered_did)
manta_utils.asset_pretty_print.print_ddo(ddo)

# %% [markdown]
# Verify that this asset exists in the MetaData storage
# %%
# ddo = ocn.metadata_store.get_asset_ddo(registered_did)
ddo = ocn.resolve_asset_did(registered_did)

# %% [markdown]
# And this is what you would expect if the DID is *NOT* in the database
# %%
random_did = 'did:op:9a3c2693c1f942b8a61cba7d212e5cd50c1b9a5299f74e39848e9b4c2148d453'
try: ocn.metadata_store.get_asset_ddo(random_did)
except Exception as e: print("This raises an error, as required:", e)

# %% [markdown]
# Similarly, we can verify that this asset is registered into the blockchain, and that you are the owner,
# congratulations on publishing an Asset into Ocean Protocol!

# %%
# We need the pure ID string (a DID without the prefixes)
asset_id = squid_py.did.did_to_id(registered_did)
owner = ocn.keeper.did_registry.contract_concise.getOwner(asset_id)
print("Asset ID", asset_id, "owned by", owner)
assert str.lower(owner) == str.lower(publisher_acct.address)


