from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from CreateAcc import main as create_account_main
from transfer import main as transfer_main
from transfer_amount import transfer_exact_amount
from deployAcc import deploy_contract as deploy_main
import json
from pydantic import BaseModel
from send_gift import send_gift  # Add this import
from stake_validator2 import main as stake_main  # Use stake_validator2.py instead of stake.py

# Add this class for request validation
class TransferRequest(BaseModel):
    address: str
    amount_strk: float

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/create-deploy")
async def create_and_deploy():
    try:
        # Step 1: Create Account
        print("\n=== 1. Creating New Account ===")
        await create_account_main()
        
        # Get the created account details
        with open('new_account.json', 'r') as f:
            account_data = json.load(f)
        
        # Step 2: Fund Account
        print("\n=== 2. Funding Account ===")
        await transfer_main()
        
        # Step 3: Deploy Account
        print("\n=== 3. Deploying Account ===")
        deploy_result = await deploy_main()
        
        # Return all relevant information
        return {
            "status": "success",
            "message": "Account created, funded, and deployed successfully",
            "data": {
                "address": account_data["address"],
                "public_key": account_data["public_key"],
                "funding_tx": account_data.get("funding_tx_hash"),
                "deployment_tx": deploy_result if deploy_result else None
            }
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_root():
    return {"status": "online", "message": "API is running"} 

@app.post("/execute-transfer")
async def execute_transfer(request: TransferRequest):
    try:
        print(f"Received transfer request: {request}")  # Log the request
        tx_hash = await transfer_exact_amount(
            to_address=request.address,
            amount_strk=request.amount_strk
        )
        print(f"Transfer successful, hash: {tx_hash}")  # Log success
        
        return {
            "status": "success",
            "message": "Transfer completed successfully",
            "transaction_hash": tx_hash
        }
        
    except Exception as e:
        print(f"Detailed transfer error: {str(e)}")  # Log detailed error
        raise HTTPException(
            status_code=500,
            detail=f"Transfer failed: {str(e)}"
        ) 

@app.post("/send-gift")
async def execute_gift(request: TransferRequest):
    try:
        print(f"\n=== Starting Gift Transfer ===")
        print(f"To address: {request.address}")
        print(f"Amount: {request.amount_strk} STRK")
        
        # Read sender's details for logging
        with open('new_account.json', 'r') as f:
            account_data = json.load(f)
        print(f"From address: {account_data['address']}")
            
        tx_hash = await send_gift(
            to_address=request.address,
            amount_strk=request.amount_strk
        )
        
        print(f"Transaction hash: {tx_hash}")
        
        return {
            "status": "success",
            "message": "Gift sent successfully! 🎁",
            "transaction_hash": tx_hash,
            "from_address": account_data['address'],
            "to_address": request.address,
            "amount": request.amount_strk
        }
        
    except Exception as e:
        print(f"\n=== Gift Transfer Error ===")
        print(f"Error type: {type(e)}")
        print(f"Error message: {str(e)}")
        print(f"Full error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send gift: {str(e)}"
        ) 

@app.post("/stake")
async def execute_stake():
    try:
        print(f"\n=== Starting Staking Process ===")
        
        # Execute the staking function and get the transaction hash
        result = await stake_main()
        
        # Convert the transaction hash to hex string if it's a number
        if isinstance(result, int):
            tx_hash = hex(result)  # Convert to hex string
        elif isinstance(result, str):
            tx_hash = result
        else:
            print(f"Warning: Unexpected transaction hash type: {type(result)}")
            raise HTTPException(
                status_code=500,
                detail="Invalid transaction hash format"
            )
        
        print(f"Transaction hash: {tx_hash}")
        
        return {
            "status": "success",
            "message": "Staking completed successfully! 🎯",
            "transaction_hash": tx_hash
        }
        
    except Exception as e:
        print(f"\n=== Staking Error ===")
        print(f"Error type: {type(e)}")
        print(f"Error message: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Staking failed: {str(e)}"
        ) 

@app.get("/get-account")
async def get_account():
    try:
        with open('new_account.json', 'r') as f:
            account_data = json.load(f)
        return account_data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Account data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 

@app.get("/get-staked-amount")
async def get_staked_amount():
    try:
        # Import your staking contract interaction code
        from stake_validator2 import get_staked_amount
        
        # Get the staked amount
        amount = await get_staked_amount()
        return {
            "status": "success",
            "staked_amount": str(amount)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get staked amount: {str(e)}"
        ) 