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
STRK_CONTRACT = "0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d"

async def send_gift(to_address, amount_strk):
    try:
        # Read the sender's details from new_account.json
        with open('new_account.json', 'r') as f:
            account_data = json.load(f)
            
        sender_address = account_data['address']
        sender_private_key = int(account_data['private_key'], 16)
        
        print(f"\nSending gift from: {sender_address}")
        
        # Initialize client
        client = FullNodeClient(node_url=NODE_URL)
        
        # Set up account
        key_pair = KeyPair.from_private_key(sender_private_key)
        account = Account(
            client=client,
            address=sender_address,
            key_pair=key_pair,
            chain=StarknetChainId.SEPOLIA
        )
        
        # Convert STRK to smallest unit (18 decimals)
        amount_wei = int(float(amount_strk) * 10**18)
        
        print(f"Sending {amount_strk} STRK to {to_address}")
        
        # Create STRK token contract instance
        contract = await Contract.from_address(STRK_CONTRACT, account)
        
        # Get current balance
        balance_response = await contract.functions["balanceOf"].call(int(sender_address, 16))
        balance = balance_response[0]
        print(f"Current sender balance: {balance / 1e18} STRK")
        
        # Add some tolerance for gas fees (0.0001 STRK)
        if balance < (amount_wei + int(0.0001 * 10**18)):
            print(f"Required: {amount_wei / 1e18} STRK")
            print(f"Available: {balance / 1e18} STRK")
            raise Exception(f"Insufficient STRK balance. Need {amount_strk} STRK plus gas fees.")
        
        # Prepare transfer
        call = contract.functions["transfer"].prepare_call(
            recipient=int(to_address, 16),
            amount=amount_wei
        )
        
        # Send transaction
        transaction = await account.sign_invoke_v3(
            calls=[call],
            auto_estimate=True
        )
        
        resp = await account.client.send_transaction(transaction)
        tx_hash = hex(resp.transaction_hash)
        print(f"Gift sent! Transaction hash: {tx_hash}")
        
        # Wait for transaction
        await account.client.wait_for_tx(resp.transaction_hash)
        print("Gift transfer complete! 🎁")
        
        return tx_hash
        
    except Exception as e:
        print(f"Error sending gift: {e}")
        raise

# Update the FastAPI endpoint to use this function
async def main():
    # Test function
    to_address = "0x0530f347bb9aad521c36d803f44957242dbf67cb52078609e3c3cfb5a82e9544"
    amount = 2.54
    await send_gift(to_address, amount)

if __name__ == "__main__":
    asyncio.run(main()) 