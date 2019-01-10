# %% [markdown]
# # Getting Underway - wallets, passwords and tokens
#
# To interact in Ocean Protocol, you will need a wallet and you will fund it with some
# Token to access the assets in the network.
#
# In this notebook, we will work with a class which *represents* a
# User of Ocean Protocol.
#
# To use Ocean, a User requires
# - A user account address
# - A password
#
# With this information, the Ocean instance can be instantiated with the Ocean.main_account attribute.
# This attribute enables the User to unlock event calls in the networks.
# This class will be used in later scripts to simulate behaviour of actors on the network.
# See the /script_fixtures directory for utilities such as the User() class

# %% [markdown]
# ### Section 0: Import modules, and setup logging
#%%
# Standard imports
import random
import logging
from pathlib import Path
import csv
# Import mantaray and the Ocean API (squid)
# mantaray_utilities is an extra helper library to simulate interactions with the Ocean API.
import squid_py
from squid_py.ocean.ocean import Ocean
from squid_py.config import Config
import mantaray_utilities as manta_utils
logging.info("Squid API version: {}".format(squid_py.__version__))
from pprint import pprint
# Setup logging to a higher level and not flood the console with debug messages
manta_utils.logging.logger.setLevel('CRITICAL')

#%%
# Get the configuration file path for this environment
# You can specify your own configuration file at any time, and pass it to the Ocean class.
# os.environ['USE_K8S_CLUSTER'] = 'true'
logging.critical("Deployment type: {}".format(manta_utils.config.get_deployment_type()))
CONFIG_INI_PATH = manta_utils.config.get_config_file_path()
logging.critical("Configuration file selected: {}".format(CONFIG_INI_PATH))

# %% [markdown]
# ## Section 1: Examine the configuration object
#%%
# The API can be configured with a file or a dictionary.
# In this case, we will instantiate from file, which you may also inspect.
# The configuration is a standard library [configparser.ConfigParser()](https://docs.python.org/3/library/configparser.html) object.
print("Configuration file:", CONFIG_INI_PATH)
configuration = Config(CONFIG_INI_PATH)
pprint(configuration._sections)

# %% [markdown]
# Let's look at the 2 parameters that define your identity
# The 20-byte 'parity.address' defines your account address
# 'parity.password' is used to decrypt your private key and securely sign transactions
#%%
print("Currently selected address:",configuration['keeper-contracts']['parity.address'])
print("Associated password:",configuration['keeper-contracts']['parity.password'])

# %% [markdown]
# ## Section 2: Instantiate the Ocean API class with this configuration
# %%
ocn = Ocean(configuration)
logging.critical("Ocean smart contract node connected ".format())

# The Ocean API, during development, queries the blockchain to return all created (simulated) accounts;
for acct in ocn.accounts:
    print(acct)

# Alternatively, the accounts are available on the keeper instance;
print(ocn.keeper.accounts)
# %% [markdown]
# The Ocean API has a 'main_account', this is the currently active (your) account.
#%%
ocn.main_account.address

#%%
# List the accounts created in the node
# ocn.accounts is a {address: Account} dict
print(len(ocn.accounts), "ocean accounts available with following addresses:")
for address in ocn.accounts:
    acct = ocn.accounts[address]
    print(acct.address)


#%%
# The configuration has a 'main account'. This is the currently active and unlocked account.

#%%
ocn.main_account.address
# %% [markdown]
# ### Section 2: From accounts, to Users
#
# A simple wrapper for each address is used to represent a user.
# See: [./script_fixtures/user.py](https://github.com/oceanprotocol/mantaray_utilities/blob/8e3128b49ec8ba00f4f8056a4c888e86b23a5c5c/mantaray_utilities/user.py#L13)

#%% [markdown]
# Users are instantiated and listed
#
# Selected accounts are unlocked via password.
# A password.csv file should be located in the project root directory, with each row containing <address>,<password>
#
# In the following cell, `num_users` specifies how many of the available acocunts will be processed.
# The script will alternate between Data Scientist and Data Owner roles.
#%%
# Create some simulated users of Ocean Protocol
# Alternate between Data Scientists (Consumers)
# and Data Owners (providers)
users = list()
num_users = 4
address_list = [acct for acct in ocn.accounts]
for i, acct_address in enumerate(address_list[0:num_users]):
    if i%2 == 0: role = 'Data Scientist'
    else: role = 'Data Owner'
    role = "User"
    if acct_address.lower() in list(PASSWORD_MAP.keys()):
        this_password = PASSWORD_MAP[acct_address]
    else:
        this_password = None

    user = manta_user.User(names.get_full_name(), role, acct_address, this_password, CONFIG_INI_PATH)
    users.append(user)

# Select only unlocked accounts
unlocked_users = [u for u in users if u.credentials]
logging.info("Selected {} unlocked accounts for simulation.".format(len(unlocked_users)))

#%%
# (Optional)
# Delete the configuration files in the /user_configurations folder
for f in Path('.').glob('user_configurations/*.ini'):
    f.unlink()

#%% [markdown]
# List the users
#%%
for u in unlocked_users: print(u)

#%% [markdown]
# ### Section 3: Filling your chest with a bounty of ERC20 token
# Get these users some Ocean token
#%%
for usr in unlocked_users:
    if usr.account.ocean_balance == 0:
        rcpt = usr.account.request_tokens(random.randint(0, 100))
        usr.ocn._web3.eth.waitForTransactionReceipt(rcpt)

#%% [markdown]
# List the users, and notice the updated balance
#%%
for u in unlocked_users: print(u)