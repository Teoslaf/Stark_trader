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

async def check_account_status(client, address):
    try:
        # Get account contract
        account_contract = await client.get_class_at(address)
        print(f"Account contract status: Active")
        return True
    except Exception as e:
        print(f"Account not yet active: {e}")
        return False

async def transfer_remaining(to_address):
    try:
        # Load account details from new_account.json
        with open('new_account.json', 'r') as f:
            account_data = json.load(f)
        
        # Initialize client
        client = FullNodeClient(node_url=os.getenv("NODE_URL"))
        
        # Set up account
        private_key = int(account_data['private_key'], 16)
        key_pair = KeyPair.from_private_key(private_key)
        account = Account(
            client=client,
            address=account_data['address'],
            key_pair=key_pair,
            chain=StarknetChainId.SEPOLIA
        )
        
        # Get and print current balance
        balance = await account.get_balance()
        print(f"\nCurrent balance: {balance / 1e18} ETH")
        
        if balance <= int(0.001 * 10**18):  # Increased to 0.001 ETH for gas
            print("Error: Insufficient balance for transfer")
            return None
            
        # Leave 0.001 ETH for gas (increased from 0.0005)
        amount_to_transfer = (balance - int(0.001 * 10**18)) 
        
        print(f"Transferring {amount_to_transfer / 1e18} ETH to {to_address}")
        
        # Create contract instance
        contract = await Contract.from_address(os.getenv("ETH_CONTRACT_ADDRESS"), account)
        
        # Prepare invoke
        call = contract.functions["transfer"].prepare_call(
            recipient=int(to_address, 16),
            amount=amount_to_transfer
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
        print(f"Error during remaining balance transfer: {e}")
        raise

async def main():
    try:
        # Replace with your target address
        target_address = "0x0530f347bb9aad521c36d803f44957242dbf67cb52078609e3c3cfb5a82e9544"  # Your target address here
        
        print("\n=== Checking Account Status and Transferring Remaining Balance ===")
        tx_hash = await transfer_remaining(target_address)
        if tx_hash:
            print(f"Remaining balance transfer complete: {tx_hash}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 