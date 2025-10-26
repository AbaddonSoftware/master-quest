import React, { useState } from "react";

const CopyUrlButton: React.FC = () => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async (): Promise<void> => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy URL:", err);
    }
  };


  return (
    <button
      onClick={handleCopy}
      className={`relative mx-1 px-0.5 rounded-md text-sm font-medium transition-colors border border-[#7b5e2a] 
        ${copied
          ? "bg-[#cde8b3] text-black"
          : "bg-[#e8d7b3] text-[#3a2c1a]  hover:bg-[#f4e0b6] active:bg-[#dac8a4]"}
      `}
    >
      {copied ? "Copied!" : "Copy URL"}
    </button>  
  );
};

export default CopyUrlButton;
