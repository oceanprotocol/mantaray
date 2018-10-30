#!/bin/bash -x
CONF_TEMPLATE=config.ini
CONF_FILE=config_local.ini
cp $CONF_TEMPLATE $CONF_FILE


market=$(docker exec -it docker_keeper-contracts_1 python -c "import sys, json; print(json.load(open('/keeper-contracts/artifacts/OceanMarket.development.json', 'r'))['address'])")
token=$(docker exec -it docker_keeper-contracts_1 python -c "import sys, json; print(json.load(open('/keeper-contracts/artifacts/OceanToken.development.json', 'r'))['address'])")
auth=$(docker exec -it docker_keeper-contracts_1 python -c "import sys, json; print(json.load(open('/keeper-contracts/artifacts/OceanAuth.development.json', 'r'))['address'])")

#result=$(docker exec -it docker_keeper-contracts_1 truffle migrate --reset | grep -P 'OceanMarket:|OceanToken:|OceanAuth:')
#values=$(echo $result | sed 's/OceanToken: /token.address=/' | sed 's/OceanMarket: /\nmarket.address=/' | sed 's/OceanAuth: /\nauth.address=/')
#token=$(echo $values | cut -d' ' -f1)
#market=$(echo $values | cut -d' ' -f2)
#auth=$(echo $values | cut -d' ' -f3)
#cp -R $KEEPERDIR/build/contracts $AQUARIUSDIR/venv/contracts
sed -i -e "/token.address =/c token.address = ${token}" $CONF_FILE
sed -i -e "/market.address =/c market.address = ${market}" $CONF_FILE
sed -i -e "/auth.address =/c auth.address = ${auth}" $CONF_FILE
#sed -i -e "/aquarius.address =/c aquarius.address=" $CONF_FILE