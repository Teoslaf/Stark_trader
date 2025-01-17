"use client";

import { Elements } from "@stripe/react-stripe-js";
import { loadStripe } from "@stripe/stripe-js";
import { PaymentForm } from "~~/components/PaymentForm";

const stripePromise = loadStripe(
  process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!
);

const PaymentPage = () => {
  const options = {
    mode: "payment",
    amount: 1099,
    currency: "usd",
  };

  return (
    <div className="flex items-center flex-col flex-grow pt-10">
      <div className="px-5">
        <div className="max-w-3xl">
          <Elements stripe={stripePromise} options={options}>
            <PaymentForm />
          </Elements>
        </div>
      </div>
    </div>
  );
};

export default PaymentPage;
