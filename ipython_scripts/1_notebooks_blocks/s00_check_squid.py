# %% [markdown]
# # Pre-sail checklist - Python API for Ocean
# With the Ocean Protocol components running, test the Squid API (Python API).
# Instantiate the API with your selected `config.ini` file, or use the default for this environment.

# %% [markdown]
# ## Import the API, `squid-py`, and a simple utilities library `mantaray_utilities`.
#%%
# Standard imports
import logging
import json
import pip_api
from pathlib import Path
import os

# Import mantaray and the Ocean API (squid)
import squid_py
from squid_py.ocean.ocean import Ocean
from squid_py import ConfigProvider
from squid_py.config import Config
import mantaray_utilities as manta_utils
manta_utils.logging.logger.setLevel('INFO')
from squid_py.keeper.web3_provider import Web3Provider

print("squid-py Ocean API version:", squid_py.__version__)

# %% [markdown]
# In order to manage the different environments Mantaray runs in, we have a series of environment variables
# which are used in the utilities library to resolve paths and keep behavior consistent. In the JupyterHub
# deployment, all of this is taken care of for you.

#%%
# Get the configuration file path for this environment
logging.critical("Deployment type: {}".format(manta_utils.config.get_deployment_type()))

# CONFIG_INI_PATH = manta_utils.config.get_config_file_path()
config_file = os.environ['OCEAN_CONFIG_PATH']
logging.critical("Configuration file selected: {}".format(config_file))

#%% [markdown]
# ## Connect to Ocean Protocal with the configuration file

#%%
# Load the configuration
# configuration = Config('.config_nile.ini')
configuration = Config(config_file)
print("Configuration loaded. Will connect to a node at: ", configuration.keeper_url)
squid_py.ConfigProvider.set_config(configuration)

# %% [markdown]
# Feel free to inspect the `configuration` object.

# %% [markdown]
# From the configuration, instantiate the Ocean object, the interface to Ocean Protocol.
# %%
# Instantiate Ocean
ocn = Ocean(configuration)

# %% [markdown]
# ## Assert that your contract ABI files match those in the test network
# The following cell performs some sanity checks on versions of smart contracts. The smart contract signatures
# are placed in an 'artifacts' folder. When you pip-install the squid-py API, these artifacts are located in the
# virtual environment, and you don't need to worry about them. For demonstration purposes, I've moved the artifacts
# into the project folder here.

from mantaray_utilities import assert_contracts
manta_utils.assert_contracts.assert_contract_ABI_versions(ocn, 'nile')
manta_utils.assert_contracts.assert_contract_code(ocn, 'nile')

# %% [markdown]
# The following cell will print some summary information of the Ocean connection.

#%%
print("***OCEAN***")
print("{} accounts".format(len(ocn.accounts._accounts)))
for i, account in enumerate(ocn.accounts._accounts):
    print(i, account.address)

#%% [markdown]
# ## Alternatively, connect to Ocean with a configuration as dictionary
