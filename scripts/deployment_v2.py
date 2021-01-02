from brownie import FlashloanV2, accounts

AAVE_LENDING_POOL_ADDRESS_PROVIDER = "0xB53C1a33016B2DC2fF3653530bfF1848a515c8c5"


def main():
    """
    Deploy a `FlashloanV2` contract from `accounts[0]`.
    """

    acct = accounts.load()  # add your keystore ID as an argument to this call

    flashloan = FlashloanV2.deploy(AAVE_LENDING_POOL_ADDRESS_PROVIDER, {"from": acct})
    return flashloan
