"use client";

import { useRouter } from "next/navigation";

export default function HomePage() {
  const router = useRouter();

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 bg-base-100">
      <h1 className="text-4xl font-bold text-center mb-8">
        Welcome to StarkGift 🎁
      </h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl w-full">
        <button
          onClick={() => router.push("/parent")}
          className="card bg-primary text-primary-content p-8 hover:scale-105 transition-transform"
        >
          <h2 className="card-title text-2xl mb-4">I'm a Parent 👨‍👩‍👧‍👦</h2>
          <p>Create and fund accounts for your children</p>
        </button>

        <button
          onClick={() => router.push("/payment")}
          className="card bg-accent text-accent-content p-8 hover:scale-105 transition-transform"
        >
          <h2 className="card-title text-2xl mb-4">I'm a Gift Giver 🎁</h2>
          <p>Send gifts to children's accounts</p>
        </button>
      </div>

      <div className="mt-12 text-center max-w-md">
        <h3 className="text-xl font-semibold mb-2">How it works</h3>
        <p className="text-base-content/80">
          Parents can create and manage accounts for their children, while
          friends and family can easily send gifts using StarkNet.
        </p>
      </div>
    </div>
  );
}
