from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.contract import Contract
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
PRIVATE_KEY = int(os.getenv('PRIVATE_KEY'), 16)
ACCOUNT_ADDRESS = int(os.getenv('WALLET_ADDRESS'), 16)
NODE_URL = os.getenv('NODE_URL')
# Update to the correct pool address from the dashboard
VALIDATOR_ADDRESS = int("0x00f5857f8976347f66a56b6da5de85784b2b12d7722eba29e1ff659cb04b57e7", 16)
AMOUNT_TO_STAKE = int(1 * 1e18)
APPROVAL_AMOUNT = int(10 * 1e18)

async def main():
    # Initialize client and account
    client = FullNodeClient(node_url=NODE_URL)
    account = Account(
        client=client,
        address=ACCOUNT_ADDRESS,
        key_pair=KeyPair.from_private_key(PRIVATE_KEY),
        chain=StarknetChainId.SEPOLIA,
    )

    try:
        print(f"\nPreparing to stake {AMOUNT_TO_STAKE / 1e18} STRK with validator {VALIDATOR_ADDRESS}...")

        # Get STRK token contract
        token_contract = await Contract.from_address(
            address=0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d,  # STRK token
            provider=account
        )

        # Check current balance and allowance
        balance = await token_contract.functions["balanceOf"].call(
            ACCOUNT_ADDRESS
        )
        print(f"\nCurrent STRK balance: {balance[0] / 1e18} STRK")
        print(f"Raw balance value: {balance[0]}")

        # Check and set approval if needed
        allowance = await token_contract.functions["allowance"].call(
            ACCOUNT_ADDRESS,
            VALIDATOR_ADDRESS  # Using the new validator address
        )
        print(f"\nCurrent allowance: {allowance[0] / 1e18} STRK")
        print(f"Raw allowance value: {allowance[0]}")

        if allowance[0] < AMOUNT_TO_STAKE:
            print(f"\nApproving {APPROVAL_AMOUNT / 1e18} STRK...")
            approve_call = await token_contract.functions["approve"].invoke_v3(
                VALIDATOR_ADDRESS,
                APPROVAL_AMOUNT,
                auto_estimate=True
            )
            await approve_call.wait_for_acceptance()
            print("Approval successful!")

        # After approval, get the validator contract and stake
        validator_contract = await Contract.from_address(
            address=VALIDATOR_ADDRESS,
            provider=account
        )

        # Debug: Print all available functions
        print("\nAvailable functions in validator contract:")
        for func_name in validator_contract.functions:
            print(f"- {func_name}")

        try:
            # Try to enter the pool (first time)
            print(f"\nAttempting to stake {AMOUNT_TO_STAKE / 1e18} STRK...")
            stake_call = await validator_contract.functions["enter_delegation_pool"].invoke_v3(
                ACCOUNT_ADDRESS,  # reward_address
                AMOUNT_TO_STAKE,  # amount
                auto_estimate=True
            )
            await stake_call.wait_for_acceptance()
            print("First time staking successful!")
            
        except Exception as e:
            if "Pool member exists" in str(e):
                # If already a member, add to existing position
                print("Already a pool member. Adding to existing position...")
                stake_call = await validator_contract.functions["add_to_delegation_pool"].invoke_v3(
                    ACCOUNT_ADDRESS,  # pool_member
                    AMOUNT_TO_STAKE,  # amount
                    auto_estimate=True
                )
                await stake_call.wait_for_acceptance()
                print("Additional staking successful!")
            else:
                # If it's a different error, raise it
                raise e

    except Exception as e:
        print(f"Error in main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 