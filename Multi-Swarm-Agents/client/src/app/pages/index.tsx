'use client';

import { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar";

const HomePage: React.FC = () => {
  const [account, setAccount] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(false);

  useEffect(() => {
    checkIfWalletIsConnected();
  }, []);

  const checkIfWalletIsConnected = async () => {
    if (typeof window !== "undefined" && window.ethereum) {
      try {
        const accounts: string[] = await window.ethereum.request({ method: "eth_accounts" });
        if (accounts.length > 0) {
          setAccount(accounts[0]);
        }
      } catch (error) {
        console.error("Error checking MetaMask connection:", error);
      }
    }
  };

  const connectWallet = async () => {
    if (typeof window !== "undefined" && window.ethereum) {
      try {
        const accounts: string[] = await window.ethereum.request({ method: "eth_requestAccounts" });
        setAccount(accounts[0]);
      } catch (error) {
        console.error("Error connecting to MetaMask:", error);
      }
    } else {
      alert("MetaMask is not installed. Please install it to use this feature.");
    }
  };

  const disconnectWallet = () => {
    setAccount(null);
  };

  return (
    <div className="flex min-h-screen">
      {/* Sidebar Toggle Button (visible only when sidebar is closed) */}
      {!sidebarOpen && (
        <button
          onClick={() => setSidebarOpen(true)}
          className="fixed top-4 left-4 z-50 p-2 bg-gray-800 text-white rounded focus:outline-none"
        >
          ☰
        </button>
      )}

      {/* Sidebar Component */}
      <Sidebar
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
        connectWallet={connectWallet}
        account={account}
        disconnectWallet={disconnectWallet}
      />

      {/* Main Content */}
      <div className="flex-1 p-8 pb-20 grid place-items-center">
        <main className="flex flex-col gap-8 items-center sm:items-start">
          <ol className="list-inside list-decimal text-sm text-center sm:text-left font-mono">
            <li>Hello, I'm Agent Builder</li>
            <li>Build your own agent</li>
            <li>Save and see your changes instantly.</li>
            <li>Let's get started!</li>
            <li>Please Sign up or login to continue.</li>
          </ol>
        </main>
      </div>
    </div>
  );
};

export default HomePage;
