import React from "react";

// Modern Logo Variations for CrossPostMe and XPostMe

// Logo 1: CrossPostMe - Geometric Cross with Modern Sans-Serif
export const CrossPostMeLogo1 = ({ size = "default" }) => {
  const sizes = {
    small: { icon: 32, text: "text-lg" },
    default: { icon: 40, text: "text-xl" },
    large: { icon: 56, text: "text-3xl" },
  };

  const currentSize = sizes[size];

  return (
    <div className="flex items-center gap-2">
      {/* Geometric cross with gradient */}
      <svg
        width={currentSize.icon}
        height={currentSize.icon}
        viewBox="0 0 40 40"
        fill="none"
      >
        <defs>
          <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#3B82F6" />
            <stop offset="100%" stopColor="#8B5CF6" />
          </linearGradient>
        </defs>
        {/* Plus/Cross symbol */}
        <rect x="16" y="4" width="8" height="32" rx="2" fill="url(#grad1)" />
        <rect x="4" y="16" width="32" height="8" rx="2" fill="url(#grad1)" />
        {/* Center dot */}
        <circle cx="20" cy="20" r="3" fill="white" />
      </svg>
      <div className={`${currentSize.text} font-bold`}>
        <span className="text-gray-900">Cross</span>
        <span className="text-blue-600">Post</span>
        <span className="text-purple-600">Me</span>
      </div>
    </div>
  );
};

// Logo 2: CrossPostMe - Arrow Network
export const CrossPostMeLogo2 = ({ size = "default" }) => {
  const sizes = {
    small: { icon: 32, text: "text-lg" },
    default: { icon: 40, text: "text-xl" },
    large: { icon: 56, text: "text-3xl" },
  };

  const currentSize = sizes[size];

  return (
    <div className="flex items-center gap-2">
      <svg
        width={currentSize.icon}
        height={currentSize.icon}
        viewBox="0 0 40 40"
        fill="none"
      >
        <defs>
          <linearGradient id="grad2" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#3B82F6" />
            <stop offset="100%" stopColor="#06B6D4" />
          </linearGradient>
        </defs>
        {/* Four arrows pointing out from center */}
        <path
          d="M20 8 L20 2 L18 4 M20 2 L22 4"
          stroke="url(#grad2)"
          strokeWidth="2.5"
          strokeLinecap="round"
        />
        <path
          d="M32 20 L38 20 L36 18 M38 20 L36 22"
          stroke="url(#grad2)"
          strokeWidth="2.5"
          strokeLinecap="round"
        />
        <path
          d="M20 32 L20 38 L18 36 M20 38 L22 36"
          stroke="url(#grad2)"
          strokeWidth="2.5"
          strokeLinecap="round"
        />
        <path
          d="M8 20 L2 20 L4 18 M2 20 L4 22"
          stroke="url(#grad2)"
          strokeWidth="2.5"
          strokeLinecap="round"
        />
        {/* Center circle */}
        <circle cx="20" cy="20" r="6" fill="url(#grad2)" />
      </svg>
      <div className={`${currentSize.text} font-bold`}>
        <span className="bg-gradient-to-r from-blue-600 to-cyan-500 bg-clip-text text-transparent">
          CrossPostMe
        </span>
      </div>
    </div>
  );
};

// Logo 3: XPostMe - Modern X with Gradient
export const XPostMeLogo1 = ({ size = "default" }) => {
  const sizes = {
    small: { icon: 32, text: "text-lg" },
    default: { icon: 40, text: "text-xl" },
    large: { icon: 56, text: "text-3xl" },
  };

  const currentSize = sizes[size];

  return (
    <div className="flex items-center gap-2">
      <svg
        width={currentSize.icon}
        height={currentSize.icon}
        viewBox="0 0 40 40"
        fill="none"
      >
        <defs>
          <linearGradient id="xgrad1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#EF4444" />
            <stop offset="50%" stopColor="#F59E0B" />
            <stop offset="100%" stopColor="#10B981" />
          </linearGradient>
        </defs>
        {/* Modern X shape */}
        <path
          d="M8 8 L32 32"
          stroke="url(#xgrad1)"
          strokeWidth="6"
          strokeLinecap="round"
        />
        <path
          d="M32 8 L8 32"
          stroke="url(#xgrad1)"
          strokeWidth="6"
          strokeLinecap="round"
        />
        <circle
          cx="20"
          cy="20"
          r="4"
          fill="white"
          stroke="url(#xgrad1)"
          strokeWidth="2"
        />
      </svg>
      <div className={`${currentSize.text} font-bold`}>
        <span className="text-red-500">X</span>
        <span className="text-orange-500">Post</span>
        <span className="text-green-500">Me</span>
      </div>
    </div>
  );
};

// Logo 4: XPostMe - Minimalist Bold X
export const XPostMeLogo2 = ({ size = "default" }) => {
  const sizes = {
    small: { icon: 32, text: "text-lg" },
    default: { icon: 40, text: "text-xl" },
    large: { icon: 56, text: "text-3xl" },
  };

  const currentSize = sizes[size];

  return (
    <div className="flex items-center gap-2">
      <div
        className="relative"
        style={{ width: currentSize.icon, height: currentSize.icon }}
      >
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 rounded-xl transform rotate-45"></div>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-white font-black text-2xl transform -rotate-45">
            X
          </span>
        </div>
      </div>
      <div className={`${currentSize.text} font-black`}>
        <span className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
          XPostMe
        </span>
      </div>
    </div>
  );
};

// Logo 5: XPostMe - Connected Nodes Style
export const XPostMeLogo3 = ({ size = "default" }) => {
  const sizes = {
    small: { icon: 32, text: "text-lg" },
    default: { icon: 40, text: "text-xl" },
    large: { icon: 56, text: "text-3xl" },
  };

  const currentSize = sizes[size];

  return (
    <div className="flex items-center gap-2">
      <svg
        width={currentSize.icon}
        height={currentSize.icon}
        viewBox="0 0 40 40"
        fill="none"
      >
        <defs>
          <linearGradient id="xgrad3" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#06B6D4" />
            <stop offset="100%" stopColor="#8B5CF6" />
          </linearGradient>
        </defs>
        {/* Connecting lines forming X */}
        <line
          x1="6"
          y1="6"
          x2="34"
          y2="34"
          stroke="url(#xgrad3)"
          strokeWidth="3"
          strokeLinecap="round"
        />
        <line
          x1="34"
          y1="6"
          x2="6"
          y2="34"
          stroke="url(#xgrad3)"
          strokeWidth="3"
          strokeLinecap="round"
        />
        {/* Corner nodes */}
        <circle cx="6" cy="6" r="4" fill="#06B6D4" />
        <circle cx="34" cy="6" r="4" fill="#3B82F6" />
        <circle cx="6" cy="34" r="4" fill="#6366F1" />
        <circle cx="34" cy="34" r="4" fill="#8B5CF6" />
        {/* Center node */}
        <circle
          cx="20"
          cy="20"
          r="5"
          fill="white"
          stroke="url(#xgrad3)"
          strokeWidth="2"
        />
      </svg>
      <div className={`${currentSize.text} font-bold`}>
        <span className="bg-gradient-to-r from-cyan-500 to-purple-600 bg-clip-text text-transparent">
          XPostMe
        </span>
      </div>
    </div>
  );
};

// Logo 6: CrossPostMe - Overlapping Circles (Network Effect)
export const CrossPostMeLogo3 = ({ size = "default" }) => {
  const sizes = {
    small: { icon: 32, text: "text-lg" },
    default: { icon: 40, text: "text-xl" },
    large: { icon: 56, text: "text-3xl" },
  };

  const currentSize = sizes[size];

  return (
    <div className="flex items-center gap-2">
      <svg
        width={currentSize.icon}
        height={currentSize.icon}
        viewBox="0 0 40 40"
        fill="none"
      >
        {/* Four overlapping circles creating a flower pattern */}
        <circle cx="20" cy="12" r="8" fill="#3B82F6" opacity="0.7" />
        <circle cx="28" cy="20" r="8" fill="#8B5CF6" opacity="0.7" />
        <circle cx="20" cy="28" r="8" fill="#EC4899" opacity="0.7" />
        <circle cx="12" cy="20" r="8" fill="#10B981" opacity="0.7" />
        {/* Center white circle */}
        <circle cx="20" cy="20" r="5" fill="white" />
      </svg>
      <div className={`${currentSize.text} font-bold`}>
        <span className="text-gray-900">Cross</span>
        <span className="text-blue-600">Post</span>
        <span className="text-pink-600">Me</span>
      </div>
    </div>
  );
};

export default {
  CrossPostMeLogo1,
  CrossPostMeLogo2,
  CrossPostMeLogo3,
  XPostMeLogo1,
  XPostMeLogo2,
  XPostMeLogo3,
};
