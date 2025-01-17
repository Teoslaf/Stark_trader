"use client";

import { useState } from "react";
import { useEthStarkAccount } from "~~/hooks/scaffold-stark/useEthStarkAccount";

export default function ParentPage() {
  const { address } = useEthStarkAccount();
  const [stakeAmount, setStakeAmount] = useState("");
  const [isStaking, setIsStaking] = useState(false);
  const [stakeError, setStakeError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<{
    message: string;
    txHash: string;
  } | null>(null);

  const handleStake = async () => {
    if (!stakeAmount || isNaN(Number(stakeAmount))) {
      setStakeError("Please enter a valid amount");
      return;
    }

    try {
      setIsStaking(true);
      setStakeError(null);
      setSuccessMessage(null);

      const response = await fetch("/api/stake", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          amount: stakeAmount,
          address: address,
        }),
      });

      if (!response.ok) {
        throw new Error("Staking failed");
      }

      const data = await response.json();
      if (!data.success) {
        throw new Error(data.error || "Staking failed");
      }

      // Clear input and show success message
      setStakeAmount("");
      setSuccessMessage({
        message: data.output,
        txHash: data.txHash,
      });
    } catch (err) {
      console.error("Staking error:", err);
      setStakeError(err instanceof Error ? err.message : "Failed to stake");
    } finally {
      setIsStaking(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-start min-h-screen p-4">
      <div className="w-full max-w-4xl">
        <div className="bg-base-200 rounded-xl p-6 mb-6">
          <h1 className="text-3xl font-bold mb-4">Parent Dashboard 👨‍👩‍👧‍👦</h1>
          <div className="stats shadow w-full bg-base-100">
            <div className="stat">
              <div className="stat-title text-base-content">Stake STRK</div>
              <div className="flex flex-col gap-2">
                <input
                  type="number"
                  placeholder="Amount to stake"
                  className="input input-bordered w-full"
                  value={stakeAmount}
                  onChange={(e) => setStakeAmount(e.target.value)}
                  disabled={isStaking}
                />
                <button
                  className={`btn btn-primary ${isStaking ? "loading" : ""}`}
                  onClick={handleStake}
                  disabled={isStaking || !stakeAmount}
                >
                  {isStaking ? "Staking..." : "Stake"}
                </button>
                {stakeError && (
                  <p className="text-error text-sm">{stakeError}</p>
                )}
                {successMessage && (
                  <div className="alert alert-success shadow-lg">
                    <div>
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="stroke-current flex-shrink-0 h-6 w-6"
                        fill="none"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth="2"
                          d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                      </svg>
                      <div>
                        <h3 className="font-bold">Staking successful! 🎯</h3>
                        <div className="text-xs">
                          <a
                            href={`https://sepolia.voyager.online/tx/${successMessage.txHash}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-primary hover:underline"
                          >
                            View Transaction ↗
                          </a>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
