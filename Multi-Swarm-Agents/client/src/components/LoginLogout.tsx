'use client';

import React from "react";

interface LoginLogoutProps {
  account: string | null;
  connectWallet: () => void;
  disconnectWallet: () => void;
  signUpWithWeb3: () => void;
}

const LoginLogout: React.FC<LoginLogoutProps> = ({
  account,
  connectWallet,
  disconnectWallet,
  signUpWithWeb3,
}) => {
  return (
    <div style={{ marginTop: "1rem" }} className="flex gap-4 items-center flex-col sm:flex-row">
      {account ? (
        <>
          <span className="text-sm sm:text-base">
            Connected: {account.slice(0, 6)}...{account.slice(-4)}
          </span>
          <button
            onClick={disconnectWallet}
            className="rounded-full bg-red-600 text-white px-4 py-2 hover:bg-red-700"
          >
            Log Off
          </button>
          <button
            onClick={signUpWithWeb3}
            className="rounded-full border border-gray-300 px-4 py-2 hover:bg-gray-200"
          >
            Sign Up with MetaMask
          </button>
        </>
      ) : (
        <button
          onClick={connectWallet}
          className="rounded-full bg-gray-700 text-white px-4 py-2 hover:bg-gray-600"
        >
          Login with MetaMask
        </button>
      )}
    </div>
  );
};

export default LoginLogout;
