import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  try {
    const { amount } = await req.json();

    // Call the FastAPI backend endpoint
    const response = await fetch('http://localhost:8000/stake', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ amount_strk: parseFloat(amount) }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Staking failed');
    }

    const data = await response.json();
    return NextResponse.json({ 
      success: true, 
      output: data.message,
      txHash: data.transaction_hash 
    });

  } catch (err) {
    console.error("Staking error:", err);
    return NextResponse.json({ error: (err as Error).message }, { status: 400 });
  }
}