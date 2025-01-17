import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function POST(request: Request) {
  try {
    const { address, amount_strk } = await request.json();

    // Make request to FastAPI backend
    const response = await fetch("http://localhost:8000/send-gift", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        address: address,
        amount_strk: amount_strk
      }),
    });

    const data = await response.json();
    console.log('Gift response:', data);

    if (!response.ok) {
      throw new Error(data.detail || 'Gift failed');
    }

    return NextResponse.json(data);

  } catch (error: unknown) {
    console.error('Gift error:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to send gift' },
      { status: 500 }
    );
  }
}