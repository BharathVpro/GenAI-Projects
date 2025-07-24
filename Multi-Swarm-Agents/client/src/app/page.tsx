'use client';

import { useState } from "react";
import Sidebar from "../components/Sidebar";
import Link from "next/link";
import React from "react";

const AboutPage: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(false);
  const [lightMode, setLightMode] = useState<boolean>(true);
  // No longer need simulated registeredAccounts once you use real registration
  // const [registeredAccounts, setRegisteredAccounts] = useState<string[]>([]);
  const [message, setMessage] = useState<string>("");

  // Real MetaMask Signup with MongoDB Registration
  const handleRegister = async () => {
    if (typeof window !== "undefined" && window.ethereum) {
      try {
        // Request accounts from MetaMask
        const accounts: string[] = await window.ethereum.request({ method: 'eth_requestAccounts' });
        const account = accounts[0];
        
        // Call the backend API route to register the user
        const res = await fetch('/api/signup', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ wallet: account }),
        });
        const data = await res.json();

        // Log received data to the console (this is from MongoDB)
        console.log("Signup response:", data);

        // Optionally display the success message on screen
        setMessage(data.message || '');

        alert(`Registered successfully with account: ${account}`);
      } catch (error) {
        console.error("Error during MetaMask signup:", error);
        alert("Signup failed. Please try again.");
      }
    } else {
      alert("MetaMask is not installed. Please install MetaMask and try again.");
    }
  };

  // Simulated sign in (untouched for now)
  const handleSignIn = async () => {
    if (typeof window !== "undefined" && window.ethereum) {
      try {
        const accounts: string[] = await window.ethereum.request({ method: 'eth_requestAccounts' });
        const account = accounts[0];
        // Here you would normally check against a real database or session
        console.log("Simulated sign in with account:", account);
        alert(`Signed in with account: ${account}`);
      } catch (error) {
        console.error("Error during MetaMask sign in:", error);
        alert("Sign in failed. Please try again.");
      }
    } else {
      alert("MetaMask is not installed. Please install MetaMask and try again.");
    }
  };

  // Keeping the Connect DB code for testing (if needed)
  const handleConnect = async () => {
    try {
      const res = await fetch('/api/server');
      const data = await res.json();
      setMessage(data.message);
      console.log(data.message);
    } catch (error) {
      setMessage("Connection failed");
      console.error("Connection failed:", error);
    }
  };

  return (
    <div className="flex min-h-screen">
      {/* Sidebar Toggle Button */}
      {!sidebarOpen && (
        <button
          onClick={() => setSidebarOpen(true)}
          className="fixed top-4 left-4 z-50 p-2 bg-gray-800 text-white rounded focus:outline-none"
        >
          ☰
        </button>
      )}

      <Sidebar
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
        connectWallet={() => {}}
        lightMode={lightMode}
        chats={[]} 
        currentChatId={0} 
        onSelectChat={(chatId) => console.log("Selected chat:", chatId)}
        onIncrementThreadId={() => console.log("Increment thread")}
      />

      <div className="flex-1 p-8 pb-20 grid place-items-center">
        <main className="flex flex-col gap-8 items-center">
          {/* Title in Center with animation */}
          <div className="relative flex-1 flex justify-center mt-10">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 600 300"
              className="w-[120%] h-auto animate-textAppear"
            >
              <text
                x="50%"
                y="50%"
                dominantBaseline="middle"
                textAnchor="middle"
                fontFamily="'Great Vibes', cursive"
                fontSize="100"
                fontWeight="bold"
                fill={lightMode ? "#000" : "#fff"}
              >
                MaxPlus AI
              </text>
            </svg>
          </div>

          {message && <p>{message}</p>}

          {/* Buttons for Sign in, Register, and Connect DB */}
          <div className="mt-6 flex gap-4">
            <button
              onClick={handleSignIn}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 focus:outline-none"
            >
              Sign with Metamask
            </button>
            <button
              onClick={handleRegister}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 focus:outline-none"
            >
              Sign up with Metamask
            </button>
            <button
              onClick={handleConnect}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 focus:outline-none"
            >
              Connect DB
            </button>
          </div>
        </main>
      </div>

      <style jsx>{`
        .animate-textAppear {
          animation: textAppear 0.8s ease-out forwards;
        }

        @keyframes textAppear {
          0% {
            opacity: 0;
            transform: translateY(50px);
            filter: blur(10px);
          }
          100% {
            opacity: 1;
            transform: translateY(0);
            filter: blur(0);
          }
        }
      `}</style>
    </div>
  );
};

export default AboutPage;
