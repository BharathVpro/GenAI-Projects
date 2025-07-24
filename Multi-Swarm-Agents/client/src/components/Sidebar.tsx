'use client';

import Link from "next/link";
import React, { useState, useEffect } from "react";

interface Chat {
  id: number;
  title: string;
}

interface SidebarProps {
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  lightMode: boolean;
  chats: Chat[];
  currentChatId: number;
  onSelectChat: (chatId: number) => void;
  onIncrementThreadId?: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  sidebarOpen,
  setSidebarOpen,
  lightMode,
  chats,
  currentChatId,
  onSelectChat,
  onIncrementThreadId,
}) => {
  const [account, setAccount] = useState<string | null>(null);

  // Wallet connection and sign-up functions remain unchanged...
  useEffect(() => {
    if (typeof window !== "undefined" && window.ethereum) {
      const handleAccountsChanged = (accounts: string[]) => {
        if (accounts.length > 0) {
          setAccount(accounts[0]);
        } else {
          setAccount(null);
        }
      };

      window.ethereum.on("accountsChanged", handleAccountsChanged);
      return () => {
        if (window.ethereum.removeListener) {
          window.ethereum.removeListener("accountsChanged", handleAccountsChanged);
        }
      };
    }
  }, []);

  return (
    <aside
      className={`fixed left-0 top-0 h-full w-64 p-6 flex flex-col gap-4 transition-transform duration-300 ${
        lightMode ? "bg-white text-black" : "bg-gray-800 text-white"
      } ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}`}
    >
      {/* Login/Logout and Sign Up Actions */}
      <div className="flex gap-4 items-center flex-col sm:flex-row mt-12">
        {account ? (
          <button
            onClick={() => setAccount(null)}
            className={`rounded-full px-4 py-2 ${
              lightMode ? "bg-gray-300 text-black" : "bg-gray-700 text-white"
            }`}
          >
            Log Off
          </button>
        ) : (
          <div className="flex gap-4 items-center flex-col sm:flex-row">
            {/* Wallet login/sign-up buttons */}
          </div>
        )}
      </div>

      {/* New Chat Button */}
      <button
        className={`w-full mt-4 py-2 text-center rounded-md font-bold text-lg transition-all ${
          lightMode ? "bg-gray-200 text-black hover:bg-gray-300" : "bg-gray-700 text-white hover:bg-gray-600"
        }`}
        onClick={() => {
          if (onIncrementThreadId) {
            onIncrementThreadId();
          } else {
            alert("+ Button Clicked! Customize this function.");
          }
        }}
      >
        +
      </button>

      {/* Chat Tabs Container: expands until it reaches the bottom (Home) */}
      <div className="chat-container flex-1 overflow-y-auto overflow-x-hidden flex flex-col gap-2">
        {chats.map((chat) => (
          <button
            key={chat.id}
            onClick={() => onSelectChat(chat.id)}
            className={`p-2 rounded transition-all duration-300 backdrop-blur-lg transform ${
              lightMode
                ? chat.id === currentChatId 
                    ? "bg-white/30 shadow-md scale-105 text-black"
                    : "bg-white/30 text-black"
                : chat.id === currentChatId 
                    ? "bg-gray-800/30 shadow-md scale-105 text-white"
                    : "bg-gray-800/30 text-white"
            }`}
          >
            {chat.title}
          </button>
        ))}
      </div>

      {/* Navigation Links */}
      <div className="flex flex-col items-center gap-4 mt-auto">
        <Link href="/">
          <span className="cursor-pointer hover:underline">Home</span>
        </Link>
        <Link href="/about">
          <span className="cursor-pointer hover:underline">About us</span>
        </Link>
        <Link href="">
          <span className="cursor-pointer hover:underline">Sign out</span>
        </Link>
      </div>

      <style jsx>{`
        /* Custom Scrollbar Styling for .chat-container */
        .chat-container::-webkit-scrollbar {
          width: 8px;
        }
        .chat-container::-webkit-scrollbar-track {
          background: transparent;
        }
        .chat-container::-webkit-scrollbar-thumb {
          background-color: ${lightMode ? 'rgba(255, 255, 255, 0.3)' : 'rgba(31, 41, 55, 0.3)'};
          border-radius: 4px;
        }
        /* Firefox scrollbar styling */
        .chat-container {
          scrollbar-width: thin;
          scrollbar-color: ${lightMode ? 'rgba(255, 255, 255, 0.3) transparent' : 'rgba(31, 41, 55, 0.3) transparent'};
        }
      `}</style>
    </aside>
  );
};

export default Sidebar;
