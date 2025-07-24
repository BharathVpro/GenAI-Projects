'use client';

import { useState } from "react";
import Sidebar from "../components/Sidebar";
import Link from "next/link";
import React from "react";

const AboutPage: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(false);

  return (
    <div className="flex min-h-screen">
      {/* Sidebar Toggle Button (shown only when sidebar is closed) */}
      {!sidebarOpen && (
        <button
          onClick={() => setSidebarOpen(true)}
          className="fixed top-4 left-4 z-50 p-2 bg-gray-800 text-white rounded focus:outline-none"
        >
          ☰
        </button>
      )}

      <Sidebar sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} connectWallet={() => {}} />

      <div className="flex-1 p-8 pb-20 grid place-items-center">
        <main className="flex flex-col gap-8 items-center sm:items-start">
          <h1 className="text-3xl font-bold">About Us</h1>
          <p>This is the About Us page.</p>
          <Link href="/">Go back Home</Link>
        </main>
      </div>
    </div>
  );
};

export default AboutPage;
