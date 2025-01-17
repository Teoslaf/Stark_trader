import { useEffect, useState, useMemo } from "react";
import { Contract, RpcProvider, Abi, constants } from "starknet";
import { useNetwork } from "@starknet-react/core";

interface StarknetEvent {
  args: {
    from: string;
    to: string;
    value: string;
  };
  timestamp: number;
  transaction_hash: string;
}

interface EventHistoryParams {
  address: string;
  abi: Abi;
  eventName: string;
  fromBlock?: string;
  toBlock?: string;
}

export function useEthStarkEventHistory({ 
  address, 
  abi, 
  eventName, 
  fromBlock = "latest-10000", 
  toBlock = "latest" 
}: EventHistoryParams) {
  const [events, setEvents] = useState<StarknetEvent[]>([]);
  const { chain } = useNetwork();
  
  const provider = useMemo(() => new RpcProvider({ 
    nodeUrl: process.env.NEXT_PUBLIC_NODE_URL!,
    chainId: chain.network === "sepolia" 
      ? constants.StarknetChainId.SN_MAIN 
      : constants.StarknetChainId.SN_SEPOLIA
  }), [chain.network]);

  const contract = useMemo(() => {
    if (!address || !provider || !abi) return undefined;
    try {
      return new Contract(
        abi as Abi,
        address,
        provider
      );
    } catch (error) {
      console.error("Contract creation error:", error);
      return undefined;
    }
  }, [address, provider, abi]);

  useEffect(() => {
    const fetchEvents = async () => {
      if (!contract) return;
      try {
        console.log("Fetching events for network:", chain.network);
        const events = await contract.getEvents({
          fromBlock,
          toBlock,
          eventName,
        });
        console.log("Found events:", events);
        setEvents(events);
      } catch (error) {
        console.error("Event fetching error:", error);
      }
    };

    fetchEvents();
  }, [contract, eventName, fromBlock, toBlock, chain.network]);

  return { events };
} 