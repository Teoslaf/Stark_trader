from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.contract import Contract
import os
from dotenv import load_dotenv

def decode_shortstring(felt):
    # Convert felt to bytes and remove null bytes
    bytes_str = felt.to_bytes(32, 'big').replace(b'\x00', b'')
    # Decode bytes to string
    return bytes_str.decode('utf-8')

# Load environment variables
load_dotenv()

# Initialize constants
PRIVATE_KEY = int(os.getenv('PRIVATE_KEY'), 16)
ACCOUNT_ADDRESS = os.getenv('WALLET_ADDRESS')
NODE_URL = os.getenv('NODE_URL')

# VESU Singleton contract address
VESU_SINGLETON = "0x69d0eca40cb01eda7f3d76281ef524cecf8c35f4ca5acc862ff128e7432964b"

# List of asset addresses from your output
ASSETS = [
    "0x7809bb63f557736e49ff0ae4a64bd8aa6ea60e3f77f26c520cb92c24e3700d3",
    "0x63d32a3fa6074e72e7a1e06fe78c46a0c8473217773e19f11d8c8cbfc4ff8ca",
    "0x27ef4670397069d7d5442cb7945b27338692de0d8896bdb15e6400cf5249f94",
    "0x2cd937c3dccd4a4e125011bbe3189a6db0419bb6dd95c4b5ce5f6d834d8996",
    "0x57181b39020af1416747a7d0d2de6ad5a5b721183136585e8774e1425efd5d2",
    "0x772131070c7d56f78f3e46b27b70271d8ca81c7c52e3f62aa868fab4b679e43"
]

# Pool ID from your output
POOL_ID = 843471078868109043994407045333485539726819752573207893362353166067597145284

async def main():
    # Initialize client and account
    client = FullNodeClient(node_url=NODE_URL)
    account = Account(
        client=client,
        address=ACCOUNT_ADDRESS,
        key_pair=KeyPair.from_private_key(PRIVATE_KEY),
        chain=StarknetChainId.SEPOLIA,
    )

    # Initialize VESU contract
    vesu_contract = await Contract.from_address(
        address=int(VESU_SINGLETON, 16),
        provider=account,
    )
    
    try:
        print(f"\nChecking pool {POOL_ID}:")
        result = await vesu_contract.functions["extension"].call(POOL_ID)
        extension = result[0]
        print(f"Pool extension address: {hex(extension)}")

        for asset_address in ASSETS:
            try:
                asset_config = await vesu_contract.functions["asset_config"].call(
                    POOL_ID, 
                    int(asset_address, 16)
                )
                print(f"\nAsset {asset_address}:")
                config_dict = asset_config[0][0]
                print(f"Total Staked: {config_dict['total_collateral_shares']}")
                print(f"Total Borrowed: {config_dict['total_nominal_debt']}")
                print(f"Max Utilization: {config_dict['max_utilization']/1e18*100}%")
                print(f"Scale: {config_dict['scale']}")

                token_contract = await Contract.from_address(
                    address=int(asset_address, 16),
                    provider=account,
                )
                
                try:
                    name = await token_contract.functions["name"].call()
                    symbol = await token_contract.functions["symbol"].call()
                    print(f"Token Name: {decode_shortstring(name[0])}")
                    print(f"Token Symbol: {decode_shortstring(symbol[0])}")
                except Exception as e:
                    print(f"Could not get token name/symbol: {e}")

            except Exception as e:
                print(f"Error checking asset {asset_address}: {e}")

    except Exception as e:
        print(f"Error fetching pool info: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

