# 🎁 StarkGift

## Overview 🚀
StarkGift is a decentralized application built on StarkNet that revolutionizes how parents can manage their children's digital assets while enabling family and friends to send gifts securely. Our platform combines a user-friendly frontend interface with a robust backend for secure blockchain interactions.

## Tech Stack 🛠️

### Frontend Technologies
- **Next.js 14**: React framework for production
- **Starknet.js**: StarkNet blockchain interaction
- **@starknet-react/core**: React hooks for StarkNet
- **TailwindCSS & DaisyUI**: Styling and components
- **TypeScript**: Type-safe development
- **Starknetkit**: Wallet connection

### Backend Technologies
- **FastAPI**: High-performance web framework for building APIs
- **Starknet.py**: Python SDK for StarkNet blockchain interaction
- **Python-dotenv**: Environment variable management
- **Uvicorn**: Lightning-fast ASGI server

### Smart Contract Integration
- StarkNet Smart Contracts
- Cairo Language Support
- Account Abstraction

## Features 📋

### Parent Dashboard
- Create and manage children's accounts
- Stake STRK tokens
- Monitor account balances
- Track transaction history

### Gift Giving
- Simple interface for sending gifts
- Transaction tracking
- Real-time status updates

### Backend Operations
- Account creation and deployment
- Secure token transfers
- Staking management
- Transaction status monitoring

## Getting Started ⚡

### Prerequisites
- Node.js (>= v18.17)
- Python 3.9+
- Yarn
- Virtual environment
- StarkNet wallet

### Frontend Installation

1. Setup frontend:
```bash
cd frontend
yarn install
cd packages/nextjs
cp .env.example .env
cd ../..
yarn start
```

### Backend Installation

1. Setup backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app:app --reload
```

## Environment Setup 🔐

### Frontend (.env.local)
```env
NEXT_PUBLIC_PROVIDER_URL=https://starknet-sepolia.blastapi.io/[YOUR-API-KEY]/rpc/v0_7
STRIPE_SECRET_KEY=sk_test
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test
```

### Backend (.env)
```env
WALLET_ADDRESS="your_wallet_address"
PRIVATE_KEY="your_private_key"
STRK_CONTRACT_ADDRESS="0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d"
ETH_CONTRACT_ADDRESS="0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"
ACCOUNT_CLASS_HASH="0x033434ad846cdd5f23eb73ff09fe6fddd568284a0fb7d1be20ee482f044dabe2"
NODE_URL="https://starknet-sepolia.blastapi.io/64168c77-3fa5-4e1e-9fe4-41675d212522/rpc/v0_7"
```

## Project Structure 📁
```
starkgift/
├── frontend/
│   ├── app/            # Next.js pages
│   ├── components/     # React components
│   ├── hooks/         # Custom hooks
│   └── styles/        # CSS styles
│
├── backend/
│   ├── app.py         # Main FastAPI application
│   ├── CreateAcc.py   # Account creation logic
│   ├── deployAcc.py   # Account deployment
│   └── stake_validator2.py # Staking functionality
```