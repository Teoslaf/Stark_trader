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
STRK_CONTRACT = "0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d"  # STRK token contract
PRIVATE_KEY = int(os.getenv("PRIVATE_KEY"), 16)
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")

async def transfer_exact_amount(to_address, amount_strk):
    print(f"\nUsing sender wallet: {WALLET_ADDRESS}")
    
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
    
    # Convert STRK to smallest unit (18 decimals)
    amount_wei = int(float(amount_strk) * 10**18)
    
    print(f"Transferring {amount_strk} STRK to {to_address}")
    
    try:
        # Create STRK token contract instance
        contract = await Contract.from_address(STRK_CONTRACT, account)
        
        # Get current STRK balance - fixed balance access
        balance_response = await contract.functions["balanceOf"].call(int(WALLET_ADDRESS, 16))
        balance = balance_response[0]  # Access first element of tuple
        print(f"Current sender STRK balance: {balance / 1e18}")
        
        if balance < amount_wei:
            raise Exception("Insufficient STRK balance for transfer")
        
        # Prepare transfer call
        call = contract.functions["transfer"].prepare_call(
            recipient=int(to_address, 16),
            amount=amount_wei
        )
        
        # Sign and send transaction
        transaction = await account.sign_invoke_v3(
            calls=[call],
            auto_estimate=True
        )
        
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
        # Read the account and payment data from file
        with open('new_account.json', 'r') as f:
            account_data = json.load(f)
        
        # Get the address and amount to send
        to_address = account_data['address']
        amount_strk = 2.54  # Get amount from JSON
        
        if not amount_strk:
            print("Error: No amount specified in new_account.json")
            return
            
        print(f"Sending {amount_strk} STRK to account: {to_address}")
        tx_hash = await transfer_exact_amount(to_address, amount_strk)
        
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