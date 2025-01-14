from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.hash.selector import get_selector_from_name
import asyncio
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

NODE_URL = os.getenv("NODE_URL")
PRIVATE_KEY = int(os.getenv("PRIVATE_KEY"), 16)
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")

async def verify_account():
    print("\nVerifying account setup...")
    
    # Initialize client
    client = FullNodeClient(node_url=NODE_URL)
    
    # Create key pair
    key_pair = KeyPair.from_private_key(PRIVATE_KEY)
    print(f"Public key from private key: {hex(key_pair.public_key)}")
    
    try:
        # Get account contract
        account_info = await client.get_class_hash_at(int(WALLET_ADDRESS, 16))
        print(f"Account exists with class hash: {hex(account_info)}")
        
        # Directly call the contract to get the public key
        selector = get_selector_from_name("get_public_key")
        
        response = await client.call_contract(
            call_function={
                "contract_address": int(WALLET_ADDRESS, 16),
                "entry_point_selector": selector,
                "calldata": []
            }
        )
        
        contract_public_key = response[0]  # Adjust based on the response structure
        print(f"Public key from contract: {hex(contract_public_key)}")
        
        # Compare public keys
        if contract_public_key == key_pair.public_key:
            print("\n✅ Account validation successful - public keys match!")
        else:
            print("\n❌ Account validation failed - public keys don't match!")
            print("The private key in .env doesn't correspond to this account.")
    
    except Exception as e:
        print(f"Error verifying account: {e}")

if __name__ == "__main__":
    asyncio.run(verify_account()) 