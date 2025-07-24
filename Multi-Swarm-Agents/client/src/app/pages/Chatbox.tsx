'use client';

import { useState, useEffect, useRef } from "react";
import Sidebar from "../components/Sidebar";
import { motion } from "framer-motion";
import Markdown from "markdown-to-jsx";

interface Chat {
  id: number;
  title: string;
}

const HomePage: React.FC = () => {
  const [lightMode, setLightMode] = useState<boolean>(false);
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(false);
  const [messages, setMessages] = useState<{ sender: string; text: string }[]>([]);
  const [input, setInput] = useState<string>("");

  // Manage chats state and current chat id
  const [chats, setChats] = useState<Chat[]>([]);
  const [currentChatId, setCurrentChatId] = useState<number | null>(null);

  const chatContainerRef = useRef<HTMLDivElement>(null);

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    // Add user message
    const userMessage = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    const currentInput = input; // store input before clearing
    setInput("");

    try {
      const res = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: currentInput }),
      });

      if (!res.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await res.json();
      const fullResponse = data.response;
      // Create an empty bot message first
      setMessages((prev) => [...prev, { sender: "bot", text: "" }]);
      const words = fullResponse.split(" ");
      // Stream the words one by one
      words.forEach((word, index) => {
        setTimeout(() => {
          setMessages((prev) => {
            const newMessages = [...prev];
            const lastIndex = newMessages.length - 1;
            newMessages[lastIndex] = {
              ...newMessages[lastIndex],
              text: (newMessages[lastIndex].text ? newMessages[lastIndex].text + " " : "") + word,
            };
            return newMessages;
          });
        }, index * 50);
      });
    } catch (error) {
      console.error("Error fetching API:", error);
      setMessages((prev) => [...prev, { sender: "bot", text: "Error fetching API" }]);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleSendMessage();
    }
  };

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  // New chat function: the new chat title is the last user input if available, else "New Chat"
  const handleNewChat = () => {
    // Look for the last non-empty user message
    const lastUserMessage = messages
      .slice()
      .reverse()
      .find((msg) => msg.sender === "user" && msg.text.trim() !== "");

    const newTitle = lastUserMessage ? lastUserMessage.text : "New Chat";

    const newChat: Chat = {
      id: chats.length + 1,
      title: newTitle,
    };

    setChats((prev) => [...prev, newChat]);
    setCurrentChatId(newChat.id);
    // Optionally, clear the messages for the new chat conversation
    setMessages([]);
  };

  // Dummy chat selection function (expand as needed)
  const handleSelectChat = (chatId: number) => {
    setCurrentChatId(chatId);
    // Here you can load messages for the selected chat if needed
  };

  return (
    <div className={`relative flex min-h-screen ${lightMode ? "bg-white text-black" : "bg-black text-white"}`}>
      {/* Navigation Bar */}
      <nav
        className={`fixed top-0 z-50 transition-all duration-300 ${
          sidebarOpen ? "left-64 w-[calc(100%-16rem)]" : "left-0 w-full"
        } ${lightMode ? "bg-white" : "bg-black"}`}
      >
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className={`fixed top-4 left-4 z-50 p-2 rounded focus:outline-none ${lightMode ? "text-black" : "text-white"}`}
          >
            ☰
          </button>
          <div className="flex-1 flex justify-center mt-10">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 300" className="w-2/5 h-auto">
              <text
                x="280"
                y="160"
                fontFamily="'Great Vibes', cursive"
                fontSize="48"
                fontWeight="bold"
                textAnchor="middle"
                fill={lightMode ? "#000" : "#fff"}
              >
                MaxPlus AI
              </text>
            </svg>
          </div>
          <div className="flex items-center">
            <label htmlFor="themeToggle" className="flex items-center cursor-pointer">
              <div className="relative">
                <input
                  id="themeToggle"
                  type="checkbox"
                  className="sr-only"
                  checked={lightMode}
                  onChange={() => setLightMode(!lightMode)}
                />
                <div className="w-10 h-4 bg-gray-400 rounded-full shadow-inner"></div>
                <div
                  className={`absolute w-6 h-6 rounded-full shadow -left-1 -top-1 transition-transform ${
                    lightMode ? "translate-x-6 bg-black" : "translate-x-0 bg-white"
                  }`}
                ></div>
              </div>
            </label>
          </div>
        </div>
      </nav>

      {/* Sidebar Component */}
      <Sidebar
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
        lightMode={lightMode}
        chats={chats}
        currentChatId={currentChatId || 0}
        onSelectChat={handleSelectChat}
        onIncrementThreadId={handleNewChat}
      />

      {/* Main Chat Window */}
      <div
        className={`flex-1 pt-20 pb-20 px-8 grid place-items-center transition-all duration-300 ${
          sidebarOpen ? "ml-64" : ""
        }`}
      >
        <main className="flex flex-col gap-8 items-center sm:items-start w-full max-w-3xl">
          <div
            ref={chatContainerRef}
            className={`w-full rounded-lg p-4 h-[calc(100vh-140px)] overflow-y-auto no-scrollbar flex flex-col ${lightMode ? "bg-white" : "bg-black"}`}
          >
            {messages.map((msg, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10, filter: "blur(5px)" }}
                animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
                transition={{ duration: 0.17, ease: "easeOut" }}
                className={`mb-2 p-2 rounded max-w-[75%] font-mono text-sm break-words ${
                  msg.sender === "user" ? "self-end ml-auto text-right" : "self-start mr-auto text-left"
                } ${lightMode ? "bg-white text-black" : "bg-black text-white"}`}
              >
                {msg.sender === "bot" ? <Markdown>{msg.text}</Markdown> : msg.text}
              </motion.div>
            ))}
          </div>
        </main>
      </div>

      {/* Input Box */}
      <div
        className={`fixed bottom-0 p-4 flex justify-center items-center transition-all duration-300 ${
          sidebarOpen ? "left-64 w-[calc(100%-16rem)]" : "left-0 w-full"
        } ${lightMode ? "bg-white" : "bg-black"}`}
      >
        <div className="flex gap-2 w-[60%] justify-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            className={`flex-1 p-2 rounded font-mono text-sm border ${
              lightMode ? "bg-white text-black border-black" : "bg-black text-white border-black"
            }`}
            placeholder="Type a message..."
          />
          <button onClick={handleSendMessage} className={`p-2 rounded font-mono text-sm ${lightMode ? "bg-white text-black" : "bg-black text-white"}`}>
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
