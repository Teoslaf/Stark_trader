from dataclasses import dataclass
from typing import List, Dict, Optional
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.contract import Contract
import os
from dotenv import load_dotenv

AMOUNT_TO_STAKE = int(1 * 1e18)  # 1 STRK with 18 decimals
APPROVAL_AMOUNT = int(10 * 1e18)  # 10x the stake amount for safety

@dataclass
class Asset:
    address: str
    name: str
    symbol: str
    decimals: int
    logo_uri: str
    vToken: str
    listed_block_number: int

@dataclass
class Pair:
    debt_asset: str
    collateral_asset: str

@dataclass
class Pool:
    pool_id: str
    pool_name: str
    assets: List[Asset]
    pairs: List[Pair]

class VesuReader:
    def __init__(self):
        load_dotenv()
        
        # Contract addresses
        self.SINGLETON = "0x69d0eca40cb01eda7f3d76281ef524cecf8c35f4ca5acc862ff128e7432964b"
        self.MULTIPLY = "0x5c25588809f1373bbe5ce3128715a4024cb5e067a0489526a9314ec02c410fc"
        self.LIQUIDATE = "0x7ca34e9fb392d4095f8f1647017a78ab4e8d50a86d258e7590c267eefd9c90b"
        self.DISTRIBUTOR = "0x05443e1b4d540b5ffc096c0d4533cc71d36ddb7bd381624ec5ce254db95cc8e9"
        
        # Initialize client and account
        self.client = FullNodeClient(node_url=os.getenv('NODE_URL'))
        self.account = Account(
            client=self.client,
            address=os.getenv('WALLET_ADDRESS'),
            key_pair=KeyPair.from_private_key(int(os.getenv('PRIVATE_KEY'), 16)),
            chain=StarknetChainId.SEPOLIA,
        )
        
        # Initialize contract
        self.contract = None
        
    async def init_contract(self):
        self.contract = await Contract.from_address(
            address=int(self.SINGLETON, 16),
            provider=self.account,
        )

    async def get_extension(self, pool_id: int) -> str:
        """Get the extension address for a pool"""
        result = await self.contract.functions["extension"].call(pool_id)
        return hex(result[0])

    async def get_asset_config(self, pool_id: int, asset: str) -> Dict:
        """Get asset configuration for a specific asset in a pool"""
        try:
            result = await self.contract.functions["asset_config_unsafe"].call(
                pool_id,
                int(asset, 16)
            )
            print(f"Raw asset config result: {result}")  # Debug print
            
            if not result or len(result) == 0:
                return {
                    'total_collateral_shares': 0,
                    'total_nominal_debt': 0,
                    'max_utilization': 0,
                    'scale': 0,
                    'fee_rate': 0
                }
            
            # Convert tuple to dictionary for easier access
            config = result[0] if isinstance(result, tuple) else result
            print(f"Config after unpacking: {config}")  # Debug print
            
            return {
                'total_collateral_shares': config[0] if len(config) > 0 else 0,
                'total_nominal_debt': config[1] if len(config) > 1 else 0,
                'max_utilization': config[2] if len(config) > 2 else 0,
                'scale': config[3] if len(config) > 3 else 0,
                'fee_rate': config[4] if len(config) > 4 else 0
            }
        except Exception as e:
            print(f"Error in get_asset_config: {e}")
            print(f"Result type: {type(result)}")
            print(f"Result value: {result}")
            raise

    async def get_ltv_config(self, pool_id: int, collateral_asset: str, debt_asset: str) -> Dict:
        """Get LTV configuration for a pair of assets"""
        result = await self.contract.functions["ltv_config"].call(
            pool_id,
            int(collateral_asset, 16),
            int(debt_asset, 16)
        )
        return result[0]

    async def get_position(self, pool_id: int, collateral_asset: str, debt_asset: str, user: str) -> Dict:
        """Get user position details"""
        result = await self.contract.functions["position_unsafe"].call(
            pool_id,
            int(collateral_asset, 16),
            int(debt_asset, 16) if debt_asset != "0x0" else 0,
            user  # Already an int, don't convert
        )
        return result[0]

    async def get_utilization(self, pool_id: int, asset: str) -> int:
        """Get asset utilization in a pool"""
        result = await self.contract.functions["utilization_unsafe"].call(
            pool_id,
            int(asset, 16)
        )
        return result[0]

    async def calculate_collateral_shares(self, pool_id: int, asset: str, collateral: int) -> int:
        """Calculate collateral shares for a given amount"""
        result = await self.contract.functions["calculate_collateral_shares_unsafe"].call(
            pool_id,
            int(asset, 16),
            collateral
        )
        return result[0]

async def main():
    # Initialize reader
    reader = VesuReader()
    await reader.init_contract()
    
    try:
        print(f"\nPreparing to stake {AMOUNT_TO_STAKE / 1e18} STRK...")
        print(f"Will approve {APPROVAL_AMOUNT / 1e18} STRK")  # Added for verification

        # First, let's check the token contract
        token_contract = await Contract.from_address(
            address=int(os.getenv('STRK_CONTRACT'), 16),
            provider=reader.account
        )
        
        # Check allowance first
        allowance = await token_contract.functions["allowance"].call(
            reader.account.address,
            0x360bac2ddf1f6d3aeea78d032acb1ec66845a6f112eecb5907ed2518f68a8c3  # vSTRK address
        )
        print(f"\nCurrent allowance: {allowance[0] / 1e18} STRK")
        print(f"Raw allowance value: {allowance[0]}")

        # Always approve with the higher amount
        print(f"\nApproving {APPROVAL_AMOUNT / 1e18} STRK...")
        approve_call = await token_contract.functions["approve"].invoke_v3(
            0x360bac2ddf1f6d3aeea78d032acb1ec66845a6f112eecb5907ed2518f68a8c3,  # vSTRK address
            APPROVAL_AMOUNT,
            auto_estimate=True
        )
        await approve_call.wait_for_acceptance()
        print("Approval successful!")

        # Get the vToken contract
        vtoken_contract = await Contract.from_address(
            address=0x360bac2ddf1f6d3aeea78d032acb1ec66845a6f112eecb5907ed2518f68a8c3,  # vSTRK address
            provider=reader.account
        )
        
        # Call deposit directly
        print("\nCalling deposit on vToken contract...")
        deposit_call = await vtoken_contract.functions["deposit"].invoke_v3(
            AMOUNT_TO_STAKE,
            reader.account.address,
            auto_estimate=True
        )
        
        print(f"Transaction sent! Hash: {deposit_call.hash}")
        await deposit_call.wait_for_acceptance()
        print("Transaction accepted!")

    except Exception as e:
        print(f"Error in main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 