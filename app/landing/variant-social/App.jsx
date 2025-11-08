import React from "react";

const PlatformIcon = ({ name }) => (
  <div className="text-center font-bold text-gray-300 tracking-wider text-xl">
    {name}
  </div>
);

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 via-blue-500 to-indigo-600 flex flex-col justify-center items-center p-4 font-sans">
      <div className="w-full max-w-md mx-auto text-center">
        {/* Main Headline */}
        <h1 className="text-5xl md:text-6xl font-extrabold text-white leading-tight shadow-text-lg mb-4">
          Post Once.
          <br />
          Sell Everywhere.
        </h1>

        {/* Sub-headline */}
        <p className="text-lg md:text-xl text-blue-200 mb-8">
          The reseller hack that saves you 10+ hours a week. Post to all
          marketplaces in seconds.
        </p>

        {/* The Main Call-to-Action Button */}
        <a
          href="http://localhost:3000/register"
          className="inline-block bg-yellow-400 text-gray-900 font-bold text-2xl px-12 py-5 rounded-full shadow-2xl transform transition-transform hover:scale-110 animate-pulse"
        >
          GET STARTED FREE
        </a>

        <p className="text-sm text-blue-100 mt-4">No credit card required.</p>
      </div>

      {/* Social Proof / Platforms Section */}
      <div className="absolute bottom-0 left-0 right-0 p-6">
        <div className="container mx-auto">
          <p className="text-center text-sm font-semibold text-blue-200 uppercase tracking-wider mb-4">
            WORKS WITH
          </p>
          <div className="flex justify-center items-center space-x-8">
            <PlatformIcon name="eBay" />
            <PlatformIcon name="Facebook" />
            <PlatformIcon name="Poshmark" />
            <PlatformIcon name="Mercari" />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
