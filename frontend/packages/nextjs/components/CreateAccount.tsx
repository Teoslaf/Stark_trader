"use client";

import { useState } from "react";

export default function CreateAccount() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [message, setMessage] = useState("");

  const handleCreateAndDeploy = async () => {
    try {
      setIsProcessing(true);
      setMessage("Creating and deploying account...");

      const response = await fetch("http://localhost:8000/create-deploy", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();

      if (data.status === "success") {
        setMessage("Account created and deployed successfully!");
      } else {
        setMessage(`Error: ${data.message}`);
      }
    } catch (error) {
      setMessage(
        `Error: ${error instanceof Error ? error.message : "Unknown error occurred"}`
      );
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="flex flex-col items-center gap-4">
      <button
        onClick={handleCreateAndDeploy}
        disabled={isProcessing}
        className="btn btn-primary disabled:opacity-50"
      >
        {isProcessing ? "Processing..." : "Create & Deploy Account"}
      </button>
      {message && (
        <p
          className={`text-sm ${message.includes("Error") ? "text-red-500" : "text-green-500"}`}
        >
          {message}
        </p>
      )}
    </div>
  );
}
