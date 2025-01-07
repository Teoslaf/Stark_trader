from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models.chains import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.hash.address import compute_address
import asyncio
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

# Constants
NODE_URL = os.getenv("NODE_URL")
ACCOUNT_CLASS_HASH = 0x04d07e40e93398ed3c76981e72dd1fd22557a78ce36c0515f679e27f0bb5bc5f

async def create_account():
    # Initialize client
    client = FullNodeClient(node_url=NODE_URL)
    
    # Generate new keypair
    key_pair = KeyPair.generate()
    print(f"Private key: {hex(key_pair.private_key)}")
    print(f"Public key: {hex(key_pair.public_key)}")
    
    # Calculate future address
    constructor_calldata = [key_pair.public_key]
    salt = key_pair.private_key
    
    address = compute_address(
        class_hash=ACCOUNT_CLASS_HASH,
        constructor_calldata=constructor_calldata,
        salt=salt
    )
    
    print(f"\nAccount will be deployed to: {hex(address)}")
    
    # Create account object
    account = Account(
        client=client,
        address=address,
        key_pair=key_pair,
        chain=StarknetChainId.SEPOLIA
    )
    
    # Save account details to file
    account_data = {
        "address": hex(address),
        "private_key": hex(key_pair.private_key),
        "public_key": hex(key_pair.public_key)
    }
    
    with open('new_account.json', 'w') as f:
        json.dump(account_data, f, indent=4)
    
    return account_data

async def main():
    try:
        result = await create_account()
        print("\nNow you need to:")
        print(f"1. Fund this address with ETH: {result['address']}")
        print(f"2. Save these details:")
        print(f"   Private key: {result['private_key']}")
        print(f"   Public key: {result['public_key']}")
        print("3. Once funded, you can deploy the account")
        print("\nAccount details have been saved to 'new_account.json'")
        
    except Exception as e:
        print(f"Error creating account: {e}")

if __name__ == "__main__":
    asyncio.run(main())