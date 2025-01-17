import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    const accountData = JSON.parse(
      fs.readFileSync(path.join(process.cwd(), '../../../backend/new_account.json'), 'utf8')
    );

    return NextResponse.json({
      address: accountData.address,
      private_key: accountData.private_key
    });
  } catch (error) {
    console.error('Error reading account data:', error);
    return NextResponse.json(
      { error: 'Failed to get account details' },
      { status: 500 }
    );
  }
} 