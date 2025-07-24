'use client';

import { useState, useEffect, useRef } from "react";
import Sidebar from "../../components/Sidebar";
import { motion } from "framer-motion";
import Markdown from "markdown-to-jsx";

type Message = { 
  sender: string; 
  text: string; 
  isHTML?: boolean; 
  htmlFile?: string, // Stores the extracted HTML filename.
};

type ChatSession = {
  id: number;
  title: string;
  messages: Message[];
};

const HomePage: React.FC = () => {
  const [lightMode, setLightMode] = useState<boolean>(false);
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(false);
  
  // Manage multiple chat sessions
  const [chats, setChats] = useState<ChatSession[]>([
    { id: 1, title: "Chat 1", messages: [] }
  ]);
  const [currentChatId, setCurrentChatId] = useState<number>(1);
  const [input, setInput] = useState<string>("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // Get the active chat session.
  const currentChat = chats.find((chat) => chat.id === currentChatId) || { id: 0, title: "", messages: [] };

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    // Append user message
    const userMessage: Message = { sender: "user", text: input };
    setChats((prev) =>
      prev.map((chat) =>
        chat.id === currentChatId ? { ...chat, messages: [...chat.messages, userMessage] } : chat
      )
    );
    const currentInput = input;
    setInput("");
    
    // Create a FormData instance to include query, thread_id and file if available.
    const formData = new FormData();
    formData.append("query", currentInput);
    formData.append("thread_id", currentChatId.toString());
    if (selectedFile) {
      formData.append("file", selectedFile);
    }

    try {
      const res = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        body: formData, // FormData sets the Content-Type automatically.
      });

      if (!res.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await res.json();
      const fullResponse: string = data.response;
      
      // Check if the response includes a public file path
      if (fullResponse.includes("../client/public/")) {
        // Extract the file name from the full path, e.g., "some_name.html"
        const htmlRegex = /..\/agentbuilder\/public\/(\S+\.html)/;
        const match = fullResponse.match(htmlRegex);
        const htmlFile = match ? match[1] : "Age_Distribution.html"; // Fallback file

        setChats((prev) =>
          prev.map((chat) =>
            chat.id === currentChatId
              ? { 
                  ...chat, 
                  messages: [...chat.messages, { sender: "bot", text: "", isHTML: true, htmlFile }]
                }
              : chat
          )
        );
      } else {
        // Append an empty bot message first so it renders on the left
        setChats((prev) =>
          prev.map((chat) =>
            chat.id === currentChatId
              ? { ...chat, messages: [...chat.messages, { sender: "bot", text: "" }] }
              : chat
          )
        );
        
        // Animate the bot message rendering word by word.
        const words = fullResponse.split(" ");
        words.forEach((word, index) => {
          setTimeout(() => {
            setChats((prev) =>
              prev.map((chat) => {
                if (chat.id === currentChatId) {
                  const newMessages = [...chat.messages];
                  const lastIndex = newMessages.length - 1;
                  const lastMessage = newMessages[lastIndex];
                  newMessages[lastIndex] = {
                    ...lastMessage,
                    text: (lastMessage.text ? lastMessage.text + " " : "") + word,
                  };
                  return { ...chat, messages: newMessages };
                }
                return chat;
              })
            );
          }, index * 50);
        });
      }
    } catch (error) {
      console.error("Error fetching API:", error);
      const errorMessage: Message = { sender: "bot", text: "Error fetching API" };
      setChats((prev) =>
        prev.map((chat) =>
          chat.id === currentChatId ? { ...chat, messages: [...chat.messages, errorMessage] } : chat
        )
      );
    } finally {
      // Clear the selected file after sending the message
      setSelectedFile(null);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleSendMessage();
    }
  };

  // Update the file upload handler to store the selected file
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      console.log("Uploaded file:", file);
      setSelectedFile(file);
    }
  };

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [currentChat.messages]);

  // Create a new chat session by updating the current chat title then adding a new session.
  const handleNewChat = () => {
    const lastUserMsg = currentChat.messages
      .filter((msg) => msg.sender === "user" && msg.text.trim() !== "")
      .pop();

    const maxTitleLength = 20;
    const updatedTitle =
      lastUserMsg && lastUserMsg.text.trim().length > 0
        ? lastUserMsg.text.trim().length > maxTitleLength
          ? lastUserMsg.text.trim().slice(0, maxTitleLength) + "..."
          : lastUserMsg.text.trim()
        : currentChat.title;

    setChats((prevChats) =>
      prevChats.map((chat) =>
        chat.id === currentChatId ? { ...chat, title: updatedTitle } : chat
      )
    );

    const newId = chats.length + 1;
    const newChat: ChatSession = { id: newId, title: "New Chat", messages: [] };
    setChats((prev) => [...prev, newChat]);
    setCurrentChatId(newId);
  };

  const handleSelectChat = (chatId: number) => {
    setCurrentChatId(chatId);
  };

  return (
    <div className={`relative flex min-h-screen ${lightMode ? "bg-white text-black" : "bg-black text-white"}`}>
      {/* Navigation Bar */}
      <nav className={`fixed top-0 z-50 transition-all duration-300 ${sidebarOpen ? "left-64 w-[calc(100%-16rem)]" : "left-0 w-full"} ${lightMode ? "bg-white" : "bg-black"}`}>
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className={`fixed top-4 left-4 z-50 p-2 rounded focus:outline-none ${lightMode ? "text-black" : "text-white"}`}
          >
            ☰
          </button>
          <div className="fixed top-4 right-4 flex items-center">
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
                  className={`absolute w-6 h-6 rounded-full shadow -left-1 -top-1 transition-transform ${lightMode ? "translate-x-6 bg-black" : "translate-x-0 bg-white"}`}
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
        chats={chats.map(({ id, title }) => ({ id, title }))}
        currentChatId={currentChatId}
        onSelectChat={handleSelectChat}
        onIncrementThreadId={handleNewChat}
      />

      {/* Main Chat Area */}
      <div className={`flex-1 pt-20 pb-20 px-8 grid place-items-center transition-all duration-300 ${sidebarOpen ? "ml-64" : ""}`}>
        <main className="flex flex-col gap-8 items-center sm:items-start w-full max-w-3xl">
          <div
            ref={chatContainerRef}
            className={`w-full rounded-lg p-4 h-[calc(100vh-140px)] overflow-y-auto no-scrollbar flex flex-col ${lightMode ? "bg-white" : "bg-black"}`}
          >
            {currentChat.messages.map((msg, index) => {
              const containerClasses = msg.isHTML
                ? "w-full p-0"
                : `mb-2 p-2 rounded max-w-[75%] font-mono text-sm break-words ${
                    msg.sender === "user" ? "self-end ml-auto text-right" : "self-start mr-auto text-left"
                  }`;
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 10, filter: "blur(5px)" }}
                  animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
                  transition={{ duration: 0.17, ease: "easeOut" }}
                  className={`${containerClasses} ${lightMode ? "bg-white text-black" : "bg-black text-white"}`}
                >
                  {msg.sender === "bot" ? (
                    msg.isHTML ? (
                      <iframe
                        src={msg.htmlFile ? `/${msg.htmlFile}` : ""}
                        className="w-full h-96 border-none"
                        title={msg.htmlFile || "Embedded Content"}
                      ></iframe>
                    ) : (
                      <Markdown>{msg.text}</Markdown>
                    )
                  ) : (
                    msg.text
                  )}
                </motion.div>
              );
            })}
          </div>
        </main>
      </div>

      {/* Input Box with Upload Button */}
      <div className={`fixed bottom-0 p-4 flex justify-center items-center transition-all duration-300 ${sidebarOpen ? "left-64 w-[calc(100%-16rem)]" : "left-0 w-full"} ${lightMode ? "bg-white" : "bg-black"}`}>
        <div className="flex gap-2 w-[60%] justify-center">
          <div className="relative flex-1">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              className={`w-full p-2 pr-10 rounded font-mono text-sm border ${lightMode ? "bg-white text-black border-black" : "bg-black text-white border-black"}`}
              placeholder="Type a message..."
            />
            {/* Upload Button using file.svg from public folder */}
            <label className="absolute right-2 top-1/2 transform -translate-y-1/2 cursor-pointer">
              <img src="/file.svg" alt="Upload File" className="h-5 w-5" />
              <input type="file" className="hidden" onChange={handleFileUpload} />
            </label>
          </div>
          <button
            onClick={handleSendMessage}
            className={`p-2 rounded font-mono text-sm ${lightMode ? "bg-white text-black" : "bg-black text-white"}`}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
