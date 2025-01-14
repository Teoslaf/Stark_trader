from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from CreateAcc import main as create_account_main
from transfer import main as transfer_main
from deployAcc import deploy_contract as deploy_main
from transfer_amount import transfer_exact_amount
import json

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

@app.post("/execute-transfer")
async def execute_transfer(request: dict):
    try:
        amount_strk = request.get("amount_strk")

        if not amount_strk:
            raise HTTPException(
                status_code=400, 
                detail="Missing amount_strk"
            )

        # Read recipient address from new_account.json
        try:
            with open('new_account.json', 'r') as f:
                account_data = json.load(f)
                to_address = account_data['address']
        except FileNotFoundError:
            raise HTTPException(
                status_code=400,
                detail="No recipient account found. Please create an account first."
            )

        print(f"Transferring {amount_strk} STRK to {to_address}")
        
        # Execute the transfer with the address from new_account.json
        result = await transfer_exact_amount(to_address, float(amount_strk))
        
        # Update the transaction hash in new_account.json
        account_data['funding_tx_hash'] = result
        with open('new_account.json', 'w') as f:
            json.dump(account_data, f, indent=4)
        
        return {
            "status": "success",
            "message": "Transfer executed successfully",
            "data": {
                "tx_hash": result["tx_hash"],
                "address": to_address,
                "amount": amount_strk
            }
        }
        
    except Exception as e:
        print(f"Transfer error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_root():
    return {"status": "online", "message": "API is running"} 