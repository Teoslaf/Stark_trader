"use client";

import React, { useCallback, useRef, useState, useEffect } from "react";
import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Bars3Icon,
  BugAntIcon,
  ChevronDownIcon,
} from "@heroicons/react/24/outline";
import { useOutsideClick } from "~~/hooks/scaffold-stark";
import { CustomConnectButton } from "~~/components/scaffold-stark/CustomConnectButton";
import { useTheme } from "next-themes";
import { SwitchTheme } from "./SwitchTheme";
import {
  useAccount,
  useConnect,
  InjectedConnector,
} from "@starknet-react/core";
import { BlockIdentifier } from "starknet";
import { connect } from "starknetkit";
import { useEthStarkAccount } from "~~/hooks/scaffold-stark/useEthStarkAccount";
import useScaffoldEthBalance from "~~/hooks/scaffold-stark/useScaffoldEthBalance";
import useScaffoldStrkBalance from "~~/hooks/scaffold-stark/useScaffoldStrkBalance";
import { BlockieAvatar } from "~~/components/scaffold-stark/BlockieAvatar";
import { Address } from "starknet";
import { Balance } from "~~/components/scaffold-stark/Balance";

type HeaderMenuLink = {
  label: string;
  href: string;
  icon?: React.ReactNode;
};

export const menuLinks: HeaderMenuLink[] = [
  {
    label: "Home",
    href: "/",
  },
];

export const HeaderMenuLinks = () => {
  const pathname = usePathname();
  const { theme } = useTheme();
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    setIsDark(theme === "dark");
  }, [theme]);

  return (
    <>
      {menuLinks.map(({ label, href, icon }) => {
        const isActive = pathname === href;
        return (
          <li key={href}>
            <Link
              href={href}
              passHref
              className={`${
                isActive
                  ? "!bg-gradient-nav !text-white active:bg-gradient-nav shadow-md"
                  : ""
              } py-1.5 px-3 text-sm rounded-full gap-2 grid grid-flow-col hover:bg-gradient-nav hover:text-white`}
            >
              {icon}
              <span>{label}</span>
            </Link>
          </li>
        );
      })}
    </>
  );
};
/**
 * Site header
 */
export const Header = () => {
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const burgerMenuRef = useRef<HTMLDivElement>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [accountData, setAccountData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const { address, isConnected, isConnecting } = useEthStarkAccount();
  const { connect } = useConnect();
  const displayAddress = accountData?.address || address;
  const ethBalance = useScaffoldEthBalance({ address: displayAddress });
  const strkBalance = useScaffoldStrkBalance({ address: displayAddress });

  useOutsideClick(
    burgerMenuRef as React.RefObject<HTMLElement>,
    useCallback(() => setIsDrawerOpen(false), [])
  );

  const createAndDeployAccount = async () => {
    try {
      setIsCreating(true);
      setError(null);

      const response = await fetch("http://localhost:8000/create-deploy", {
        method: "POST",
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setAccountData(data.data);

      // Connect with just the connector instance
      const connector = new InjectedConnector({
        options: {
          id: "braavos",
          name: "Braavos",
        },
      });
      await connect({ connector });
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to connect account"
      );
      console.error("Error:", err);
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <div className="lg:static top-0 navbar min-h-0 flex-shrink-0 justify-between z-20 px-0 sm:px-2">
      <div className="navbar-start w-auto lg:w-1/2 -mr-2">
        <div className="lg:hidden dropdown" ref={burgerMenuRef}>
          <label
            tabIndex={0}
            className={`ml-1 btn btn-ghost ${isDrawerOpen ? "hover:bg-secondary" : "hover:bg-transparent"}`}
            onClick={() =>
              setIsDrawerOpen((prevIsOpenState) => !prevIsOpenState)
            }
          >
            <Bars3Icon className="h-1/2" />
          </label>
          {isDrawerOpen && (
            <ul
              tabIndex={0}
              className="menu menu-compact dropdown-content mt-3 p-2 shadow rounded-box w-52 bg-base-100"
              onClick={() => setIsDrawerOpen(false)}
            >
              <HeaderMenuLinks />
            </ul>
          )}
        </div>
        <Link
          href="/"
          passHref
          className="hidden lg:flex items-center gap-2 ml-4 mr-6 shrink-0"
        ></Link>
        <ul className="hidden lg:flex lg:flex-nowrap menu menu-horizontal px-1 gap-2">
          <HeaderMenuLinks />
        </ul>
      </div>
      <div className="navbar-end flex-grow mr-2 gap-4">
        <div className="flex gap-3 items-center">
          {!address ? (
            <button
              className="btn btn-sm px-2 py-[0.35rem] dropdown-toggle gap-0 !h-auto border border-[#5c4fe5]"
              onClick={createAndDeployAccount}
              disabled={isCreating}
            >
              {isCreating ? (
                <>
                  <span className="loading loading-spinner loading-sm"></span>
                  <span className="ml-2 mr-2 text-sm">Creating...</span>
                </>
              ) : (
                <>
                  <BlockieAvatar
                    address={
                      address
                        ? (`0x${(address as string).substring(2)}` as `0x${string}`)
                        : "0x"
                    }
                    size={28}
                  />
                  <span className="ml-2 mr-2 text-sm">Create Account</span>
                </>
              )}
            </button>
          ) : (
            <div className="flex items-center gap-4">
              <Balance address={displayAddress as Address} />
              <details className="dropdown dropdown-end leading-3">
                <summary className="btn bg-transparent btn-sm px-2 py-[0.35rem] dropdown-toggle gap-0 !h-auto border border-[#5c4fe5]">
                  <BlockieAvatar
                    address={
                      `0x${displayAddress?.substring(2)}` as `0x${string}`
                    }
                    size={28}
                  />
                  <span className="ml-2 mr-2 text-sm">
                    {displayAddress?.slice(0, 6)}...{displayAddress?.slice(-4)}
                  </span>
                  <ChevronDownIcon className="h-6 w-4 ml-2 sm:ml-0 sm:block hidden" />
                </summary>
              </details>
            </div>
          )}
          {!address && <CustomConnectButton />}
        </div>
        <SwitchTheme className={`pointer-events-auto`} />
      </div>
    </div>
  );
};
