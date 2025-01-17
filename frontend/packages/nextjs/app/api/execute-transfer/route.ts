import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function POST(request: Request) {
  try {
    const { amount_strk } = await request.json();

    if (!amount_strk) {
      return NextResponse.json(
        { message: 'Missing required parameters' },
        { status: 400 }
      );
    }

    // Read address from new_account.json
    const accountData = JSON.parse(
      fs.readFileSync(path.join(process.cwd(), '../../../backend/new_account.json'), 'utf8')
    );

    const address = accountData.address;

    // Make request to FastAPI backend
    const response = await fetch("http://localhost:8000/execute-transfer", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        address: address,
        amount_strk: amount_strk
      }),
    });

    console.log('Response status:', response.status);
    const data = await response.json();
    console.log('Response data:', data);

    if (data.status === "success") {
      return NextResponse.json({
        message: 'Transfer successful',
        data: data
      });
    } else {
      return NextResponse.json(
        { message: data.message || 'Transfer failed' },
        { status: 400 }
      );
    }

  } catch (error) {
    console.error('Transfer error:', error);
    return NextResponse.json(
      {
        message: 'Transfer failed',
        error: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}