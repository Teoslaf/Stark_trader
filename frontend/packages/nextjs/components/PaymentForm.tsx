"use client";

import { useState, useEffect } from "react";
import {
  PaymentElement,
  useStripe,
  useElements,
} from "@stripe/react-stripe-js";
import { CheckCircleIcon } from "@heroicons/react/24/solid";
import { useAccount } from "../hooks/useAccount";
import { useRouter } from "next/navigation";

interface PaymentSuccessData {
  recipientAddress: string;
  transactionId: string;
  amount: string;
}

export const PaymentForm = () => {
  const router = useRouter();
  const stripe = useStripe();
  const elements = useElements();
  const { account } = useAccount();
  const [amount, setAmount] = useState<number>(10);
  const [tokenPrice, setTokenPrice] = useState<number>(0);
  const [tokenAmount, setTokenAmount] = useState<number>(0);
  const [clientSecret, setClientSecret] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [paymentDetails, setPaymentDetails] = useState({
    transactionId: "",
    strkAmount: "",
    address: "",
  });
  const [recipientAddress, setRecipientAddress] = useState<string>("");
  const [paymentData, setPaymentData] = useState<{
    transactionId: string;
    tokenAmount: string;
    address: string;
  } | null>(null);
  const [paymentId, setPaymentId] = useState("");

  // Fetch token price
  useEffect(() => {
    fetch("/api/price/STRK")
      .then((res) => res.json())
      .then((data) => {
        const price = data.starknet.usd;
        setTokenPrice(price);
        // Calculate STRK tokens: USD amount / STRK price
        setTokenAmount(amount / price);
      })
      .catch((err) => console.error("Error fetching price:", err));
  }, [amount]);

  // Fetch client secret when amount changes
  useEffect(() => {
    if (amount > 0) {
      fetch("/api/create-payment-intent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ amount: Math.round(amount * 100) }), // Convert to cents
      })
        .then((res) => res.json())
        .then((data) => {
          setClientSecret(data.clientSecret);
        })
        .catch((err) => {
          setErrorMessage(err.message);
        });
    }
  }, [amount]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!stripe || !elements || !clientSecret) {
      setErrorMessage("Payment not ready. Please try again.");
      return;
    }

    setIsLoading(true);
    try {
      const { error: submitError } = await elements.submit();
      if (submitError) throw submitError;

      const { error, paymentIntent } = await stripe.confirmPayment({
        elements,
        clientSecret,
        confirmParams: {
          return_url: `${window.location.origin}/`,
        },
        redirect: "if_required",
      });

      if (error) {
        setErrorMessage(error.message || "Payment failed");
      } else if (paymentIntent && paymentIntent.status === "succeeded") {
        setPaymentId(paymentIntent.id || "");

        try {
          const transferResponse = await fetch("/api/execute-transfer", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              amount_strk: amount * 2.54,
            }),
          });

          if (!transferResponse.ok) {
            throw new Error("Transfer failed");
          }

          const transferData = await transferResponse.json();
          console.log("Transfer successful:", transferData);
          setShowSuccessModal(true);
        } catch (error) {
          console.error("Transfer error:", error);
          setErrorMessage("Payment succeeded but token transfer failed");
        }
      }
    } catch (error) {
      console.error("Payment error:", error);
      setErrorMessage(
        error instanceof Error ? error.message : "Payment failed"
      );
    }
    setIsLoading(false);
  };

  const paymentElementOptions = {
    layout: "tabs",
    defaultValues: {
      billingDetails: {
        name: "",
        email: "",
      },
    },
    business: {
      name: "STRK Token Purchase",
    },
  };

  const appearance = {
    theme: "night",
    variables: {
      colorPrimary: "#5c4fe5",
    },
  };

  return (
    <>
      <form
        onSubmit={handleSubmit}
        className="max-w-md mx-auto p-6 bg-base-200 rounded-xl shadow-lg"
      >
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">Amount (USD)</label>
          <input
            type="number"
            min="1"
            value={amount || ""}
            onChange={(e) => {
              const val = e.target.value;
              setAmount(val ? Number(val) : 0);
            }}
            className="w-full p-2 border rounded"
          />
          <p className="text-sm text-gray-500 mt-1">
            You will receive approximately {tokenAmount.toFixed(2)} STRK
            {tokenPrice > 0 && ` (1 STRK = $${tokenPrice.toFixed(2)})`}
          </p>
        </div>

        <PaymentElement
          options={paymentElementOptions}
          className="bg-base-100 rounded-lg p-4"
        />

        <button
          type="submit"
          disabled={!stripe || isLoading || !clientSecret}
          className="btn btn-primary w-full mt-4"
        >
          {!clientSecret
            ? "Loading..."
            : isLoading
              ? "Processing..."
              : `Pay $${amount}`}
        </button>

        {errorMessage && (
          <div className="text-error mt-4 text-center">{errorMessage}</div>
        )}
      </form>

      {showSuccessModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-base-200 p-8 rounded-xl max-w-md w-full mx-4">
            <div className="text-center">
              <div className="text-success text-5xl mb-4">✓</div>
              <h3 className="text-2xl font-bold mb-4">Payment Successful!</h3>
              <p className="mb-4">Thank you for your purchase.</p>
              <div className="bg-base-300 rounded-lg p-4 mb-6 text-left">
                <p className="text-sm mb-2">Transaction ID: {paymentId}</p>
                <p className="text-sm mb-2">Amount: ${amount}</p>
                <p className="text-sm">STRK Amount: {amount * 2.54}</p>
              </div>
              <button
                className="btn btn-primary w-full"
                onClick={() => {
                  setShowSuccessModal(false);
                  router.push("/gift");
                }}
              >
                View Your Gift
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default PaymentForm;
