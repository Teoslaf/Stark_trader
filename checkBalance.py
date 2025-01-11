from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.contract import Contract
import asyncio
from starknet_py.net.account.account import Account
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.net.models import StarknetChainId
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get environment variables
NODE_URL = os.getenv("NODE_URL")
# WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")
WALLET_ADDRESS = "0x75642f63d8eab5519e7130d929844b40cf102553ed3a3359ceef1a7beada861"
STRK_CONTRACT_ADDRESS = os.getenv("STRK_CONTRACT_ADDRESS")
ETH_CONTRACT_ADDRESS = os.getenv("ETH_CONTRACT_ADDRESS")

async def get_token_balance(client, contract_address, wallet_address):
    try:
        contract = await Contract.from_address(contract_address, client)
        response = await contract.functions["balanceOf"].call(wallet_address)
        # Convert balance to readable units (assuming 18 decimals)
        return response["balance"] / (10 ** 18)
    except Exception as e:
        print(f"Error fetching balance for contract {contract_address}: {e}")
        return 0

async def main():
    # Initialize client with Sepolia
    client = FullNodeClient(node_url=NODE_URL)
    
    try:
        # Create account instance
        account = Account(
            client=client,
            address=WALLET_ADDRESS,
            key_pair=KeyPair(private_key=0, public_key=0),
            chain=StarknetChainId.SEPOLIA,
        )
        
        # Get ETH balance
        eth_balance = await account.get_balance()
        eth_balance_in_eth = eth_balance / (10 ** 18)
        
        # Get STRK balance
        strk_balance = await account.get_balance(STRK_CONTRACT_ADDRESS)
        strk_balance_in_strk = strk_balance / (10 ** 18)
        
        print(f"Wallet: {WALLET_ADDRESS}")
        print(f"ETH Balance: {eth_balance_in_eth} ETH")
        print(f"STRK Balance: {strk_balance_in_strk} STRK")
    except Exception as e:
        print(f"Error getting balance: {e}")

if __name__ == "__main__":
    asyncio.run(main())
