import asyncio
from dotenv import load_dotenv
import os

# Import the correct functions from each file
from CreateAcc import main as create_account_main
from transfer import main as transfer_main
from deployAcc import deploy_contract as deploy_main

async def main():
    try:
        print("\n=== 1. Creating New Account ===")
        await create_account_main()
        
        print("\n=== 2. Funding Account ===")
        await transfer_main()
        
        print("\n=== 3. Deploying Account ===")
        await deploy_main()
        
        print("\n=== All operations completed successfully! ===")
        
    except Exception as e:
        print(f"\nError during process: {e}")
        return False
    
    return True

if __name__ == "__main__":
    load_dotenv()
    success = asyncio.run(main())
    if not success:
        print("\nProcess did not complete successfully")