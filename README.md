# Aave Flash Loan Brownie Mix

![Aave Banner](box-img-sm.png)

*Adapted from [aave/flashloan-box](https://github.com/aave/flashloan-box) by [mrdavey](https://github.com/mrdavey/).*

This Brownie mix comes with everything you need to start [developing on flash loans](https://docs.aave.com/developers/tutorials/performing-a-flash-loan/...-in-your-project).

This mix is configured for use with [Ganache](https://github.com/trufflesuite/ganache-cli) on a [forked mainnet](https://eth-brownie.readthedocs.io/en/stable/network-management.html#using-a-forked-development-network).

## Installation and Setup

1. [Install Brownie](https://eth-brownie.readthedocs.io/en/stable/install.html), if you haven't already.

2. Sign up for [Infura](https://infura.io/) and generate an API key. Store it in the `WEB3_INFURA_PROJECT_ID` environment variable.

```bash
export WEB3_INFURA_PROJECT_ID=YourProjectID
```

3. Sign up for [Etherscan](www.etherscan.io) and generate an API key. This is required for fetching source codes of the mainnet contracts we will be interacting with. Store the API key in the `ETHERSCAN_TOKEN` environment variable.

```bash
export ETHERSCAN_TOKEN=YourApiToken
```

4. Download the mix.

```bash
brownie bake aave-flashloan
```

## Basic Use

To perform a simple flash loan in a development environment:

1. Open the Brownie console. This automatically launches Ganache on a forked mainnet.

```bash
$ brownie console
```

2. Create variables for the Aave lending pool and ETH reserve addresses. These were obtained from the Aave [reserve addresses](https://docs.aave.com/developers/developing-on-aave/deployed-contract-instances#reserves-assets) documentation.

```python
>>> aave_lending_pool = "0x24a42fD28C976A61Df5D00D0599C34c4f90748c8"
>>> eth_reserve = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
```

3. Deploy the [`Flashloan.sol`](contracts/Flashloan.sol) contract.

```python
>>> flashloan = Flashloan.deploy(aave_lending_pool, {"from": accounts[0]})
Transaction sent: 0xc8a35b3ecbbed196a344ed6b5c7ee6f50faf9b7eee836044d1c7ffe10093ef45
  Gas price: 0.0 gwei   Gas limit: 6721975
  Flashloan.constructor confirmed - Block: 9995378   Gas used: 796934 (11.86%)
  Flashloan deployed at: 0x3194cBDC3dbcd3E11a07892e7bA5c3394048Cc87
```

4. Transfer some Ether to the newly deployed contract. We must do this because we have not implemented any custom flash loan logic, otherwise the loan will fail from an inability to pay the fee.

```python
>>> accounts[0].transfer(flashloan, "1 ether")
Transaction sent: 0xa70b90eb9a9899e8f6e709c53a436976315b4279c4b6797d0a293e169f94d5b4
  Gas price: 0.0 gwei   Gas limit: 6721975
  Transaction confirmed - Block: 9995379   Gas used: 21055 (0.31%)
```

5. Now we are ready to perform our first flash loan!

```python
>>> tx = flashloan.flashloan(eth_reserve, {"from": accounts[0]})
Transaction sent: 0x1e2a6ce4e749f8c01aef9f747b65f6a63a9945d4e8331e8269c000d3c6779644
  Gas price: 0.0 gwei   Gas limit: 6721975
  Flashloan.flashloan confirmed - Block: 9995380   Gas used: 183858 (2.74%)
```

## Implementing Flash Loan Logic

[`contracts/Flashloan.sol`](contracts/Flashloan.sol) is where you implement your own logic for flash loans. In particular:

* The size of the loan is set in line 39 in `flashloan`.
* Custom flash loan logic is added after line 23 in `executeOperation`.

See the Aave documentation on [Performing a Flash Loan](https://docs.aave.com/developers/tutorials/performing-a-flash-loan) for more detailed information.

## Testing

To run the tests:

```
brownie test
```

The example tests provided in this mix start by transfering funds to the [`Flashloan.sol`](contracts/Flashloan.sol) contract. This ensures that the loan executes succesfully without any custom logic. Once you have built your own logic, you should edit [`tests/test_flashloan.py`](tests/test_flashloan.py) and remove this initial funding logic.

See the [Brownie documentation](https://eth-brownie.readthedocs.io/en/stable/tests-pytest-intro.html) for more detailed information on testing your project.

## Debugging Failed Transactions

Use the `--interactive` flag to open a console immediatly after each failing test:

```
brownie test --interactive
```

Within the console, transaction data is available in the [`history`](https://eth-brownie.readthedocs.io/en/stable/api-network.html#txhistory) container:

```python
>>> history
[<Transaction '0x50f41e2a3c3f44e5d57ae294a8f872f7b97de0cb79b2a4f43cf9f2b6bac61fb4'>,
 <Transaction '0xb05a87885790b579982983e7079d811c1e269b2c678d99ecb0a3a5104a666138'>]
```

Examine the [`TransactionReceipt`](https://eth-brownie.readthedocs.io/en/stable/api-network.html#transactionreceipt) for the failed test to determine what went wrong. For example, to view a traceback:

```python
>>> tx = history[-1]
>>> tx.traceback()

Traceback for '0xb05a87885790b579982983e7079d811c1e269b2c678d99ecb0a3a5104a666138':
Trace step 393, program counter 961:
  File "contracts/Flashloan.sol", line 42, in Flashloan.flashloan:
    lendingPool.flashLoan(address(this), _asset, amount, data);
Trace step 430, program counter 119:
  File "InitializableAdminUpgradeabilityProxy-flattened.sol", line 884, in InitializableAdminUpgradeabilityProxy:
    _fallback();
Trace step 482, program counter 818:
  File "InitializableAdminUpgradeabilityProxy-flattened.sol", line 937, in Proxy._fallback:
    _delegate(_implementation());
Trace step 494, program counter 1943:
  File "InitializableAdminUpgradeabilityProxy-flattened.sol", line 979, in BaseUpgradeabilityProxy._upgradeTo:
    emit Upgraded(newImplementation);
Trace step 2071, program counter 8750:
  File "LendingPool-flattened.sol", line 5850, in LendingPool.flashLoan:
    receiver.executeOperation(_reserve, _amount, amountFee, _params);
Trace step 2278, program counter 1652:
  File "contracts/Flashloan.sol", line 31, in Flashloan.executeOperation:
    transferFundsBackToPoolInternal(_reserve, totalDebt);
Trace step 2470, program counter 2417:
  File "contracts/aave/FlashLoanReceiverBase.sol", line 26, in FlashLoanReceiverBase.transferFundsBackToPoolInternal:
    transferInternal(core, _reserve, _amount);
Trace step 2568, program counter 3064:
  File "contracts/aave/FlashLoanReceiverBase.sol", line 32, in FlashLoanReceiverBase.transferInternal:
    require(success == true, "Couldn't transfer ETH");
```

To view a tree map of how the transaction executed:

```python
>>> tx.call_trace()

Call trace for '0xb05a87885790b579982983e7079d811c1e269b2c678d99ecb0a3a5104a666138':
Flashloan.flashloan 0:2606  (0x3194cBDC3dbcd3E11a07892e7bA5c3394048Cc87)
├─LendingPoolAddressesProvider.getLendingPool 144:240  (0x24a42fD28C976A61Df5D00D0599C34c4f90748c8)
└─InitializableAdminUpgradeabilityProxy 394:2594  (0x398eC7346DcD622eDc5ae82352F02bE94C62d119)
  └─Proxy._fallback 431:2594
    ├─BaseAdminUpgradeabilityProxy._willFallback 435:470
    │ └─BaseUpgradeabilityProxy._setImplementation 440:468
    ├─BaseAdminUpgradeabilityProxy._admin 475:477
    └─BaseUpgradeabilityProxy._upgradeTo 483:2589
      └─LendingPool.flashLoan 495:2581  (0x6D252BaEa75459Ed0077410613c5f6e51cAb4750)
        ├─InitializableAdminUpgradeabilityProxy 764:995  (0x3dfd23A6c5E8BbcFc9581d2E864a68feb6a076d3)
        │ ├─Proxy._fallback 801:995
        │ │ ├─BaseAdminUpgradeabilityProxy._willFallback 805:840
        │ │ │ └─BaseUpgradeabilityProxy._setImplementation 810:838
        │ │ ├─BaseAdminUpgradeabilityProxy._admin 845:847
        │ │ └─BaseUpgradeabilityProxy._upgradeTo 853:991
        │ │   └─LendingPoolCore.getReserveIsActive 865:983  (0x5766067108e534419ce13F05899bC3E3F4344948)
        ├─EthAddressLib.ethAddress 1042:1046
        ├─InitializableAdminUpgradeabilityProxy 1133:1308  (0xeAC99f8Fb1996AeB153E8cF0842908973a48C66F)
        │ ├─Proxy._fallback 1170:1308
        │ │ ├─BaseAdminUpgradeabilityProxy._willFallback 1174:1209
        │ │ │ └─BaseUpgradeabilityProxy._setImplementation 1179:1207
        │ │ ├─BaseAdminUpgradeabilityProxy._admin 1214:1216
        │ │ └─BaseUpgradeabilityProxy._upgradeTo 1222:1304
        │ │   └─LendingPoolParametersProvider.getFlashLoanFeesInBips 1234:1296  (0xe800542e56208aC5c496A57926FA7647ed8E5f07)
        ├─SafeMath.mul 1351:1380
        ├─SafeMath.div 1386:1409
        ├─SafeMath.mul 1422:1451
        ├─SafeMath.div 1457:1480
        ├─InitializableAdminUpgradeabilityProxy 1607:1930  (0x3dfd23A6c5E8BbcFc9581d2E864a68feb6a076d3)
        │ ├─Proxy._fallback 1650:1930
        │ │ ├─BaseAdminUpgradeabilityProxy._willFallback 1654:1689
        │ │ │ └─BaseUpgradeabilityProxy._setImplementation 1659:1687
        │ │ ├─BaseAdminUpgradeabilityProxy._admin 1694:1696
        │ │ └─BaseUpgradeabilityProxy._upgradeTo 1702:1926
        │ │   └─LendingPoolCore.transferToUser 1714:1918  (0x5766067108e534419ce13F05899bC3E3F4344948)
        │ │     ├─EthAddressLib.ethAddress 1827:1831
        │ │     └─Flashloan 1873:1886  (0x3194cBDC3dbcd3E11a07892e7bA5c3394048Cc87)
        └─Flashloan.executeOperation 2072:2569  (0x3194cBDC3dbcd3E11a07892e7bA5c3394048Cc87)
          ├─FlashLoanReceiverBase.getBalanceInternal 2207:2238
          ├─SafeMath.add 2253:2271
          └─FlashLoanReceiverBase.transferFundsBackToPoolInternal 2279:2569
            ├─LendingPoolAddressesProvider.getLendingPoolCore 2329:2441  (0x24a42fD28C976A61Df5D00D0599C34c4f90748c8)
            └─FlashLoanReceiverBase.transferInternal 2471:2569
```

See the [Brownie documentation](https://eth-brownie.readthedocs.io/en/stable/core-transactions.html) for more detailed information on debugging failed transactions.

## Deployment

When you are finished testing and ready to deploy to the mainnet:

1. [Import a keystore](https://eth-brownie.readthedocs.io/en/stable/account-management.html#importing-from-a-private-key) into Brownie for the account you wish to deploy from.
2. Edit [`scripts/deployment.py`](scripts/deployment.py) and add your keystore ID according to the comments.
3. Run the deployment script on the mainnet using the following command:

```bash
$ brownie run deployment --network mainnet
```

You will be prompted to enter your keystore password, and then the contract will be deployed.

## Known issues

### No access to archive state errors

If you are using Ganache to fork a network, then you may have issues with the blockchain archive state every 30 minutes. This is due to your node provider (i.e. Infura) only allowing free users access to 30 minutes of archive state. To solve this, upgrade to a paid plan, or simply restart your ganache instance and redploy your contracts.

## Troubleshooting

See our [Troubleshooting Errors](https://docs.aave.com/developers/tutorials/troubleshooting-errors) documentation.

# Resources

 - Aave [flash loan documentation](https://docs.aave.com/developers/tutorials/performing-a-flash-loan)
 - Aave [Developer Discord channel](https://discord.gg/CJm5Jt3)
 - Brownie [Gitter channel](https://gitter.im/eth-brownie/community)
