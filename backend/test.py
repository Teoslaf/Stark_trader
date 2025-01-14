import asyncio
from checkBalance import main as check_balance
from CreateAcc import main as create_account

async def main():
    print("=== Testing Account Creation ===")
    await create_account()
    
    print("\n=== Testing Balance Check ===")
    await check_balance()

if __name__ == "__main__":
    asyncio.run(main()) 