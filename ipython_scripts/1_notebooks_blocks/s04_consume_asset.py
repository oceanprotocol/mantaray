# %% [markdown]
# Getting Underway - Downloading Datasets (Assets)
# To complete the basic datascience workflow, this notebook will demonstrate how a user
# can download an asset. Downloading an asset is a simple example of a Service Execution Agreement -
# similar to a contract with a series of clauses. Each clause is secured on the blockchain, allowing for trustful
# execution of a contract.
#
# In this notebook, an asset will be first published as before, and then ordered and downloaded.

# %% [markdown]
# ### Section 0: Import modules, and setup logging

#%%
import json
import logging
import os

from ocean_keeper import Keeper
from ocean_keeper.utils import get_account
from ocean_utils.agreements.service_types import ServiceTypes
from squid_py import Ocean
import squid_py

# Setup logging
from util.events import subscribe_event

from util import logging as manta_logging, config
from util.misc import get_metadata_example

manta_logging.logger.setLevel('INFO')
from squid_py import Config
from pathlib import Path
import web3

# Load metadata example
metadata = get_metadata_example()

#%% Add a file handler
# path_log_file = Path.home() / '{}.log'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
# fh = logging.FileHandler(path_log_file)
# fh.setLevel(logging.DEBUG)

# %% [markdown]
# ## Section 1: Get the configuration from the INI file

#%%
# Get the configuration file path for this environment
OCEAN_CONFIG_PATH = Path(os.path.expanduser(os.environ['OCEAN_CONFIG_PATH']))
assert OCEAN_CONFIG_PATH.exists(), "{} - path does not exist".format(OCEAN_CONFIG_PATH)

# The Market Place will be delegated to provide access to your assets, so we need the address
MARKET_PLACE_PROVIDER_ADDRESS = os.environ['MARKET_PLACE_PROVIDER_ADDRESS']

logging.critical("Configuration file selected: {}".format(OCEAN_CONFIG_PATH))
logging.critical("Deployment type: {}".format(config.get_deployment_type()))
logging.critical("Squid API version: {}".format(squid_py.__version__))
logging.info("MARKET_PLACE_PROVIDER_ADDRESS:{}".format(MARKET_PLACE_PROVIDER_ADDRESS))
#%%
# Instantiate Ocean with the default configuration file.
configuration = Config(OCEAN_CONFIG_PATH)
squid_py.ConfigProvider.set_config(configuration)
ocn = Ocean(configuration)

#%% [markdown]
# ## Section 2: Delegate access of your asset to the marketplace
# When we publish a register a DDO to a marketplace, we assign several services and conditions on those services.
# By default, the permission to grant access will lie with you, the publisher. As a publisher, you would need to
# run the services component (brizo), in order to manage access to your assets.
#
# However, for the case of a marketplace, we will delegate permission to grant access to these services to the market
# place on our behalf. Therefore, we will need the public address of the marketplace component. Of course, the
# conditions are defined ultimately by you, the publisher.

#%%
MARKET_PLACE_PROVIDER_ADDRESS = web3.Web3.toChecksumAddress(MARKET_PLACE_PROVIDER_ADDRESS)

#%% [markdown]
# ## Section 3: Instantiate Ocean
#%%
keeper = Keeper.get_instance()

# %% [markdown]
# ## Section 4: Get Publisher and register an asset for testing the download
# Of course, you can download your own asset, one that you have created, or
# one that you have found via the search api. All you need is the DID of the asset.

#%%
publisher_account = get_account(1)

# publisher_account = get_account_from_config(config_from_ini, 'parity.address', 'parity.password')
print("Publisher address: {}".format(publisher_account.address))
print("Publisher   ETH: {:0.1f}".format(ocn.accounts.balance(publisher_account).eth/10**18))
print("Publisher OCEAN: {:0.1f}".format(ocn.accounts.balance(publisher_account).ocn/10**18))

#%%
# Register an asset
ddo = ocn.assets.create(metadata, publisher_account, providers=[MARKET_PLACE_PROVIDER_ADDRESS])
logging.info(f'registered ddo: {ddo.did}')
asset_price = int(ddo.metadata['main']['price']) / 10**18
asset_name = ddo.metadata['main']['name']
print("Registered {} for {} OCN".format(asset_name, asset_price))

# %% [markdown]
# ## Section 5: Get Consumer account, ensure token balance
#%%
# consumer_account = get_account_from_config(config_from_ini, 'parity.address1', 'parity.password1')
consumer_account = get_account(0)
print("Consumer address: {}".format(consumer_account.address))
print("Consumer   ETH: {:0.1f}".format(ocn.accounts.balance(consumer_account).eth/10**18))
print("Consumer OCEAN: {:0.1f}".format(ocn.accounts.balance(consumer_account).ocn/10**18))
# assert ocn.accounts.balance(consumer_account).eth/10**18 > 1, "Insufficient ETH in account {}".format(consumer_account.address)
# Ensure the consumer always has enough Ocean Token (with a margin)
if ocn.accounts.balance(consumer_account).ocn/10**18 < asset_price + 1:
    logging.info("Insufficient Ocean Token balance for this asset!".format())
    refill_amount = int(15 - ocn.accounts.balance(consumer_account).ocn/10**18)
    logging.info("Requesting {} tokens".format(refill_amount))
    ocn.accounts.request_tokens(consumer_account, refill_amount)

# %% [markdown]
# ## Section 6: Initiate the agreement for accessing (downloading) the asset, wait for condition events
# %%
agreement_id = ocn.assets.order(
    ddo.did,
    ddo.get_service(ServiceTypes.ASSET_ACCESS).index,
    consumer_account
)
logging.info("Consumer has placed an order for asset {}".format(ddo.did))
logging.info("The service agreement ID is {}".format(agreement_id))

# %% [markdown]
# In Ocean Protocol, downloading an asset is enforced by a contract.
# The contract conditions and clauses are set by the publisher. Conditions trigger events, which are monitored
# to ensure the contract is successfully executed.

# %%
subscribe_event("created agreement", keeper, agreement_id)
subscribe_event("lock reward", keeper, agreement_id)
subscribe_event("access secret store", keeper, agreement_id)
subscribe_event("escrow reward", keeper, agreement_id)

# %% [markdown]
# Now wait for all events to complete!

# %% [markdown]
# Now that the agreement is signed, the consumer can download the asset.

#%%
assert ocn.agreements.is_access_granted(agreement_id, ddo.did, consumer_account.address)
# ocn.agreements.status(agreement_id)
ocn.assets.consume(agreement_id, ddo.did, 'Access', consumer_account, 'downloads_nile')

logging.info('Success buying asset.')
