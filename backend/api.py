from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId
from starknet_py.contract import Contract
from starknet_py.net.account.account import Account
from starknet_py.net.signer.stark_curve_signer import KeyPair
from pathlib import Path

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/create-account")
async def create_account():
    try:
        print("Starting account creation...")
        # Generate a new keypair
        keypair = KeyPair.generate_random()
        private_key = keypair.private_key
        public_key = keypair.public_key

        print(f"Generated keypair - Public key: {public_key}")

        # Save account details
        account_data = {
            "private_key": str(private_key),
            "public_key": str(public_key),
            "address": None  # Will be set after deployment
        }

        # Ensure the file path exists
        file_path = Path('new_account.json')
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Save to file
        print(f"Saving account data to {file_path.absolute()}")
        with open(file_path, 'w') as f:
            json.dump(account_data, f, indent=2)

        print("Account creation successful")
        return {"message": "Account created successfully", "data": account_data}
    except Exception as e:
        print(f"Error creating account: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to create account: {str(e)}")

@app.post("/deploy-account")
async def deploy_account():
    try:
        # Read account data
        with open('new_account.json', 'r') as f:
            account_data = json.load(f)

        # Deploy account contract
        # Add your deployment logic here
        # This is a placeholder - you'll need to add actual deployment code
        account_address = "0x7acbca603147483f56f170dc242809d9aa03210e7be98c175a5e6af40278622"

        # Update account data with address
        account_data["address"] = account_address
        with open('new_account.json', 'w') as f:
            json.dump(account_data, f)

        return {"message": "Account deployed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/fund-account")
async def fund_account():
    try:
        # Read account data
        with open('new_account.json', 'r') as f:
            account_data = json.load(f)

        # Add your funding logic here
        # This is a placeholder - you'll need to add actual funding code

        return {"message": "Account funded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-account-details")
async def get_account_details():
    try:
        with open('new_account.json', 'r') as f:
            account_data = json.load(f)
        return account_data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Account not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 