import React from "react";

const Logo = ({ className = "", size = "default", showText = true }) => {
  const sizes = {
    small: { icon: 32, text: "text-lg" },
    default: { icon: 40, text: "text-xl" },
    large: { icon: 56, text: "text-3xl" },
  };

  const currentSize = sizes[size] || sizes.default;

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {/* Overlapping Circles - Network Effect Design */}
      <svg
        width={currentSize.icon}
        height={currentSize.icon}
        viewBox="0 0 40 40"
        fill="none"
      >
        {/* Four overlapping circles creating a flower pattern - representing 4 platforms */}
        <circle cx="20" cy="12" r="8" fill="#3B82F6" opacity="0.7" />
        <circle cx="28" cy="20" r="8" fill="#8B5CF6" opacity="0.7" />
        <circle cx="20" cy="28" r="8" fill="#EC4899" opacity="0.7" />
        <circle cx="12" cy="20" r="8" fill="#10B981" opacity="0.7" />
        {/* Center white circle - represents unified platform */}
        <circle cx="20" cy="20" r="5" fill="white" />
      </svg>
      {showText && (
        <div className={`${currentSize.text} font-bold`}>
          <span className="text-blue-600">Cross</span>
          <span className="text-purple-600">Post</span>
          <span className="text-pink-600">Me</span>
        </div>
      )}
    </div>
  );
};

export default Logo;
