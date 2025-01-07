from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models.chains import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.contract import Contract
import asyncio
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

# Constants
NODE_URL = os.getenv("NODE_URL")
ETH_CONTRACT = os.getenv("ETH_CONTRACT_ADDRESS")
PRIVATE_KEY = int(os.getenv("PRIVATE_KEY"), 16)
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")

async def transfer_eth(to_address, amount_eth=0.01):
    print("\nUsing sender wallet:", WALLET_ADDRESS)
    
    # Initialize client
    client = FullNodeClient(node_url=NODE_URL)
    
    # Set up account
    key_pair = KeyPair.from_private_key(PRIVATE_KEY)
    account = Account(
        client=client,
        address=WALLET_ADDRESS,
        key_pair=key_pair,
        chain=StarknetChainId.SEPOLIA
    )
    
    # Convert ETH to Wei
    amount_wei = int(amount_eth * 10**18)
    
    print(f"Transferring {amount_eth} ETH to {to_address}")
    
    try:
        # Get current balance
        balance = await account.get_balance()
        print(f"Current sender balance: {balance / 1e18} ETH")
        
        # Create contract instance
        contract = await Contract.from_address(ETH_CONTRACT, account)
        
        # Prepare call
        call = contract.functions["transfer"].prepare_call(
            recipient=int(to_address, 16),
            amount=amount_wei
        )
        
        # Sign the transaction
        transaction = await account.sign_invoke_v3(
            calls=[call],
            auto_estimate=True
        )
        
        # Send the transaction
        resp = await account.client.send_transaction(transaction)
        tx_hash = hex(resp.transaction_hash)
        print(f"Transaction hash: {tx_hash}")
        
        # Wait for transaction
        await account.client.wait_for_tx(resp.transaction_hash)
        print("Transfer complete!")
        
        return tx_hash
        
    except Exception as e:
        print(f"Error during transfer: {e}")
        raise

async def main():
    try:
        # Read the new account address from file
        with open('new_account.json', 'r') as f:
            account_data = json.load(f)
        
        # Get the address to send to
        to_address = account_data['address']
        
        print(f"Sending ETH to newly created account: {to_address}")
        tx_hash = await transfer_eth(to_address)
        
        # Save transaction hash to the JSON file
        account_data['funding_tx_hash'] = tx_hash
        with open('new_account.json', 'w') as f:
            json.dump(account_data, f, indent=4)
        
        print(f"\nTransaction hash saved to new_account.json")
        
    except FileNotFoundError:
        print("Error: Please run CreateAcc.py first to generate the account")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 