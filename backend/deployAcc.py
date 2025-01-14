from starknet_py.net.account.account import Account
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Constants
NODE_URL = os.getenv("NODE_URL")
ACCOUNT_CLASS_HASH = "0x04d07e40e93398ed3c76981e72dd1fd22557a78ce36c0515f679e27f0bb5bc5f"

async def deploy_contract():
    # Load account details from JSON
    with open('new_account.json', 'r') as file:
        account_data = json.load(file)
    
    # Initialize KeyPair from private key
    private_key = int(account_data['private_key'], 16)
    key_pair = KeyPair.from_private_key(private_key)
    
    # Connect to StarkNet
    client = FullNodeClient(node_url=NODE_URL)
    
    # Deploy the account contract with reduced max fee
    deployment = await Account.deploy_account_v1(
        address=int(account_data['address'], 16),
        class_hash=int(ACCOUNT_CLASS_HASH, 16),
        salt=private_key,
        key_pair=key_pair,
        client=client,
        constructor_calldata=[key_pair.public_key],
        max_fee=int(0.001 * 1e18)  # Reduced from 1e16 to 0.001 ETH
    )
    
    # Wait for transaction
    await deployment.wait_for_acceptance()
    
    # Update status in JSON file
    account_data['status'] = 'deployed'
    with open('new_account.json', 'w') as file:
        json.dump(account_data, file, indent=4)
    
    print(f"Account deployed successfully!")
    print(f"Transaction hash: {hex(deployment.hash)}")

# Run the deployment
if __name__ == "__main__":
    import asyncio
    asyncio.run(deploy_contract())