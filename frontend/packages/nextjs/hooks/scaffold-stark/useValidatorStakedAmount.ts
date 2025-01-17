import { useReadContract } from "@starknet-react/core";

export const useValidatorStakedAmount = (userAddress?: string) => {
  const validatorAddress = "0x0afbf5857f8976347f66a56b6da5de85784b2b12d7722eba29e1ff659cb04b57e7";
  
  const response = useReadContract({
    address: validatorAddress,
    abi: [
      {
        name: "pool_member_info",
        type: "function",
        inputs: [
          { name: "pool_member", type: "felt252" }
        ],
        outputs: [
          { name: "shares", type: "felt252" },
          { name: "reward_debt", type: "felt252" },
          { name: "pending_rewards", type: "felt252" },
          { name: "reward_address", type: "felt252" }
        ],
        stateMutability: "view"
      }
    ],
    functionName: "pool_member_info",
    args: userAddress ? [userAddress] : undefined,
    watch: true,
  });

  console.log("Debug Staking:", {
    userAddress,
    validatorAddress,
    response: response.data,
    error: response.error
  });

  return {
    ...response,
    data: response.data ? response.data[0] : undefined,
    error: response.error ? `Error: ${response.error.message || 'Unknown error'}` : null
  };
}; 