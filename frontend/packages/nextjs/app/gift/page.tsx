"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useEthStarkAccount } from "~~/hooks/scaffold-stark/useEthStarkAccount";
import {
  UserCircleIcon,
  ClockIcon,
  PlusCircleIcon,
  CurrencyDollarIcon,
} from "@heroicons/react/24/outline";

// Add this type for contacts
type Contact = {
  name: string;
  address: string;
  amount: number;
  lastUsed?: Date;
};

// Add this mapping near the top of your component
const starknetIdMap: { [key: string]: string } = {
  "tom.stark":
    "0x0530f347bb9aad521c36d803f44957242dbf67cb52078609e3c3cfb5a82e9544",
  // Add more mappings as needed
};

export default function WalletPage() {
  const [showPrivateKey, setShowPrivateKey] = useState(false);
  const [showTomGift, setShowTomGift] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [accountData, setAccountData] = useState<any>(null);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [showErrorModal, setShowErrorModal] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [txHash, setTxHash] = useState("");
  const { address } = useEthStarkAccount();
  const router = useRouter();
  const [selectedContact, setSelectedContact] = useState<Contact | null>(null);
  const [newAddress, setNewAddress] = useState("");
  const [newAmount, setNewAmount] = useState("");
  const [customAmount, setCustomAmount] = useState("");
  const [isValidAddress, setIsValidAddress] = useState(true);
  const [showAmountInput, setShowAmountInput] = useState(false);

  const validateAddress = (address: string) => {
    // Check for Starknet hex address
    const isHexAddress = address.startsWith("0x") && address.length === 66;
    // Check for .stark domain
    const isStarkDomain = address.toLowerCase().endsWith(".stark");

    return isHexAddress || isStarkDomain;
  };

  // Example contacts - you can replace this with your own data source
  const contacts: Contact[] = [
    {
      name: "Tom",
      address:
        "0x0530f347bb9aad521c36d803f44957242dbf67cb52078609e3c3cfb5a82e9544",
      amount: 2.4,
      lastUsed: new Date("2024-01-16"),
    },
    {
      name: "Alice",
      address:
        "0x04a69af1ef2d19c4e7ef379f6ff4c1a36e78d10fd5c8f96f0ea41012052a8e7c",
      amount: 1.8,
      lastUsed: new Date("2024-01-15"),
    },
    // Add more contacts as needed
  ];

  // Fetch account data when component mounts
  useEffect(() => {
    const fetchAccountData = async () => {
      try {
        const response = await fetch("http://localhost:8000/get-account", {
          method: "GET",
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        setAccountData(result);
      } catch (error) {
        console.error("Error fetching account data:", error);
      }
    };

    fetchAccountData();
  }, []);

  const handleNewAddress = async () => {
    if (!newAddress || !newAmount || !isValidAddress) return;

    try {
      setIsLoading(true);
      // Resolve .stark domain to address if needed
      const resolvedAddress =
        starknetIdMap[newAddress.toLowerCase()] || newAddress;

      // Call the existing /send-gift endpoint
      const response = await fetch("http://localhost:8000/send-gift", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          address: resolvedAddress,
          amount_strk: parseFloat(newAmount),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to send gift");
      }

      setTxHash(data.transaction_hash);
      setShowSuccessModal(true);

      // Update UI with the sent gift details
      const newContact: Contact = {
        name: newAddress.endsWith(".stark")
          ? newAddress.split(".")[0]
          : "Custom Address",
        address: resolvedAddress,
        amount: parseFloat(newAmount),
        lastUsed: new Date(),
      };

      setSelectedContact(newContact);
    } catch (error: any) {
      console.error("Error sending gift:", error);
      setErrorMessage(error.message || "Failed to send gift");
      setShowErrorModal(true);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendGift = async () => {
    if (!selectedContact) return;

    try {
      setIsLoading(true);
      const response = await fetch("http://localhost:8000/send-gift", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          address: selectedContact.address,
          amount_strk: selectedContact.amount,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to send gift");
      }

      setTxHash(data.transaction_hash);
      setShowSuccessModal(true);
    } catch (error: any) {
      console.error("Error sending gift:", error);
      setErrorMessage(error.message || "Failed to send gift");
      setShowErrorModal(true);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAmountChange = (amount: string) => {
    const parsedAmount = parseFloat(amount);
    if (selectedContact && !isNaN(parsedAmount)) {
      setSelectedContact({
        ...selectedContact,
        amount: parsedAmount,
      });
    }
    setCustomAmount(amount);
  };

  // Success Modal
  const SuccessModal = () => (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-[#2a3454] rounded-3xl p-6 max-w-md w-full mx-4">
        <h3 className="text-2xl font-bold text-white mb-4">
          Gift Sent Successfully! 🎁
        </h3>
        <p className="text-gray-300 mb-6">
          Your gift of {selectedContact?.amount || newAmount} STRK has been sent
          to{" "}
          {selectedContact?.name ||
            (newAddress.endsWith(".stark")
              ? newAddress
              : `${newAddress.slice(0, 6)}...${newAddress.slice(-4)}`)}
        </p>
        <a
          href={`https://sepolia.voyager.online/tx/${txHash}`}
          target="_blank"
          rel="noopener noreferrer"
          className="block w-full bg-[#1a1f38] text-white py-2 rounded-xl mb-4 text-center hover:bg-[#252b4a] transition-all"
        >
          View on Voyager 🔍
        </a>
        <button
          onClick={() => setShowSuccessModal(false)}
          className="w-full bg-yellow-400 text-black py-2 rounded-xl font-medium hover:bg-yellow-500 transition-all"
        >
          Close
        </button>
      </div>
    </div>
  );

  // Error Modal
  const ErrorModal = () => (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-[#2a3454] rounded-3xl p-6 max-w-md w-full mx-4">
        <h3 className="text-2xl font-bold text-red-400 mb-4">
          Gift Sending Failed ⚠️
        </h3>
        <p className="text-gray-300 mb-6">{errorMessage}</p>
        <button
          onClick={() => setShowErrorModal(false)}
          className="w-full bg-red-500 text-white py-2 rounded-xl font-medium hover:bg-red-600 transition-all"
        >
          Close
        </button>
      </div>
    </div>
  );

  // If showing Tom's gift page
  if (showTomGift) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-[#1a1f38]">
        <div className="max-w-md w-full bg-[#2a3454] rounded-3xl p-6 mx-4">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-3xl font-bold text-white">Send Your Gift</h1>
            <button
              onClick={() => setShowTomGift(false)}
              className="text-gray-400 hover:text-white transition-colors"
            >
              ← Back
            </button>
          </div>

          {/* Send to New Address */}
          <div className="bg-[#1a1f38] rounded-2xl p-6 mb-4">
            <h3 className="text-xl font-bold text-white mb-4">
              Forget about wallets—simply send the gift effortlessly!
            </h3>
            <div className="space-y-4">
              <div>
                <label className="text-gray-300 text-sm mb-1 block">
                  Recipient Address or Starknet ID
                </label>
                <input
                  type="text"
                  placeholder="0x... or .stark"
                  value={newAddress}
                  onChange={(e) => {
                    setNewAddress(e.target.value);
                    setIsValidAddress(validateAddress(e.target.value));
                  }}
                  className={`w-full bg-[#2a3454] text-white p-3 rounded-xl border ${
                    isValidAddress ? "border-gray-600" : "border-red-500"
                  } focus:outline-none focus:border-yellow-400`}
                />
                {!isValidAddress && newAddress && (
                  <p className="text-red-500 text-sm mt-1">
                    Please enter a valid Starknet address
                  </p>
                )}
              </div>
              <div>
                <label className="text-gray-300 text-sm mb-1 block">
                  Amount (STRK)
                </label>
                <input
                  type="number"
                  placeholder="0.0"
                  value={newAmount}
                  onChange={(e) => setNewAmount(e.target.value)}
                  className="w-full bg-[#2a3454] text-white p-3 rounded-xl border border-gray-600 focus:outline-none focus:border-yellow-400"
                  min="0"
                  step="0.1"
                />
              </div>
              <button
                onClick={handleNewAddress}
                disabled={
                  !isValidAddress || !newAddress || !newAmount || isLoading
                }
                className={`w-full flex items-center justify-center gap-2 p-3 rounded-xl transition-all
                  ${
                    isValidAddress && newAddress && newAmount && !isLoading
                      ? "bg-yellow-400 hover:bg-yellow-500 text-black"
                      : "bg-gray-600 text-gray-400 cursor-not-allowed"
                  }
                `}
              >
                {isLoading ? (
                  <>
                    <svg
                      className="animate-spin h-5 w-5 text-black"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      ></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                    <span>Sending Gift...</span>
                  </>
                ) : (
                  <>
                    <PlusCircleIcon className="w-5 h-5" />
                    <span>Send Gift 🎁</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Gift Info */}
          {selectedContact && (
            <div className="bg-[#1a1f38] rounded-2xl p-6">
              <h3 className="text-xl font-bold text-white mb-4">
                About this Gift
              </h3>
              <div className="space-y-3 text-gray-300">
                <p>
                  • You're sending{" "}
                  <span className="text-white font-bold">
                    {selectedContact.amount} STRK
                  </span>{" "}
                  to{" "}
                  <span className="text-white font-bold">
                    {selectedContact.name ||
                      (selectedContact.address.endsWith(".stark")
                        ? selectedContact.address
                        : `${selectedContact.address.slice(0, 6)}...${selectedContact.address.slice(-4)}`)}
                  </span>
                </p>
                <p>• This gift will help them get started with Starknet</p>
                <p>• Transaction fees are covered! 🎉</p>
              </div>
            </div>
          )}

          {/* Success/Error Modals */}
          {showSuccessModal && <SuccessModal />}
          {showErrorModal && <ErrorModal />}
        </div>
      </div>
    );
  }

  // Default wallet details view
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-[#1a1f38]">
      <div className="max-w-md w-full bg-[#2a3454] rounded-3xl p-6 mx-4">
        <h1 className="text-3xl font-bold text-white mb-6 flex items-center gap-2">
          🎉 Send Your Gift
        </h1>

        {/* Wallet Details Section */}
        <div className="bg-[#1a1f38] rounded-2xl p-4 mb-4">
          <h2 className="text-2xl font-bold text-white mb-4">Wallet Details</h2>

          <div className="space-y-2">
            <p className="text-white">Address:</p>
            <p className="text-white text-sm break-all">
              {accountData?.address || "Loading..."}
            </p>
            <button
              onClick={() =>
                window.open(
                  `https://sepolia.voyager.online/tx/${accountData?.funding_tx_hash || ""}`,
                  "_blank"
                )
              }
              className="w-full bg-[#2a3454] text-white py-2 rounded-xl mt-1 hover:bg-[#3a4464] transition-all"
            >
              View on Voyager 🔍
            </button>
          </div>

          <div className="mt-4 space-y-2">
            <p className="text-white">Private Key:</p>
            <p className="text-white text-sm font-mono break-all bg-[#1a1f38] p-3 rounded-lg">
              {showPrivateKey
                ? accountData?.private_key || "Loading..."
                : "••••••••••••••••"}
            </p>
            <button
              onClick={() => setShowPrivateKey(!showPrivateKey)}
              className="w-full bg-yellow-400 text-black py-2 rounded-xl font-medium hover:bg-yellow-500 transition-all"
            >
              {showPrivateKey ? "Hide Private Key 🫣" : "Reveal Private Key 👀"}
            </button>
          </div>
        </div>

        {/* Next Steps Section */}
        <div className="bg-[#1a1f38] rounded-2xl p-4 mb-4">
          <h2 className="text-2xl font-bold text-white mb-4">Next Steps</h2>
          <ol className="list-decimal list-inside space-y-2 text-white">
            <li>Save these details securely</li>
            <li>Import the wallet into your preferred Starknet wallet</li>
            <li>Your STRK tokens are ready to use!</li>
          </ol>
        </div>

        {/* What the heck button */}
        <button
          onClick={() => setShowTomGift(true)}
          className="w-full bg-yellow-400 text-black py-3 rounded-xl font-bold mb-2 hover:bg-yellow-500 transition-all"
        >
          What the heck is a wallet? 🤔
        </button>
      </div>
    </div>
  );
}
