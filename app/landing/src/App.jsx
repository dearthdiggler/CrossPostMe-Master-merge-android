import React from "react";

// --- SVG Icons (Heroicons) ---
const MobileIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    className="h-6 w-6 mr-2 inline-block"
    fill="none"
    viewBox="0 0 24 24"
    stroke="currentColor"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M12 18h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"
    />
  </svg>
);

const WebIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    className="h-6 w-6 mr-2 inline-block"
    fill="none"
    viewBox="0 0 24 24"
    stroke="currentColor"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9V3m0 18a9 9 0 009-9M3 12h18M3 12a9 9 0 019-9m-9 9a9 9 0 009 9"
    />
  </svg>
);

// --- Reusable Components ---
const Feature = ({ title, children }) => (
  <div className="bg-white bg-opacity-10 backdrop-filter backdrop-blur-lg rounded-xl p-6 border border-gray-700 shadow-lg">
    <h3 className="text-xl font-bold mb-3 text-white">{title}</h3>
    <p className="text-gray-300">{children}</p>
  </div>
);

const HowItWorksStep = ({ number, title, children }) => (
  <div className="flex items-start">
    <div className="flex items-center justify-center h-12 w-12 rounded-full bg-blue-600 text-white font-bold text-2xl mr-6">
      {number}
    </div>
    <div>
      <h3 className="text-xl font-bold text-white mb-2">{title}</h3>
      <p className="text-gray-300">{children}</p>
    </div>
  </div>
);

function App() {
  return (
    <div className="bg-gray-900 text-white font-sans">
      {/* --- Header -- */}
      <header className="fixed w-full bg-gray-900 bg-opacity-80 backdrop-filter backdrop-blur-lg z-50 border-b border-gray-800">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <div className="text-2xl font-bold tracking-wider">CrossPostMe</div>
          <nav className="space-x-4 flex items-center">
            <a
              href="http://localhost:3000/login"
              className="hidden md:inline text-gray-300 hover:text-white transition-colors"
            >
              Log In
            </a>
            <a
              href="http://localhost:3000/register"
              className="bg-blue-600 text-white px-5 py-2 rounded-full font-semibold hover:bg-blue-700 transition-transform hover:scale-105"
            >
              Register for Web App
            </a>
          </nav>
        </div>
      </header>

      {/* --- Hero Section -- */}
      <main className="pt-32 pb-20 text-center bg-gradient-to-b from-gray-900 to-gray-800">
        <div className="container mx-auto px-6">
          <h1 className="text-4xl md:text-6xl font-extrabold leading-tight mb-4">
            One Post. Every Marketplace.
          </h1>
          <p className="text-lg md:text-xl text-gray-400 mb-8 max-w-3xl mx-auto">
            Stop wasting time copying and pasting. With CrossPostMe, your
            listings go live on eBay, Facebook Marketplace, and more—all from
            one place.
          </p>
          <div className="flex justify-center items-center space-x-4 mb-12">
            <a
              href="#download"
              className="bg-white text-gray-900 px-8 py-4 rounded-full font-bold text-lg hover:bg-gray-200 transition-transform hover:scale-105 flex items-center"
            >
              <MobileIcon /> Download App
            </a>
            <a
              href="http://localhost:3000/"
              className="border-2 border-gray-500 text-gray-200 px-8 py-4 rounded-full font-bold text-lg hover:bg-gray-800 hover:border-gray-400 transition-colors flex items-center"
            >
              <WebIcon /> Use Web Version
            </a>
          </div>
          <div className="relative mt-16 max-w-5xl mx-auto">
            <div className="absolute inset-0 bg-blue-500 rounded-full blur-3xl opacity-20"></div>
            <img
              src="https://i.ibb.co/6yvjV2V/app-mockup.png"
              alt="CrossPostMe Dashboard Mockup"
              className="relative rounded-xl shadow-2xl border-4 border-gray-700"
            />
          </div>
        </div>
      </main>

      {/* --- How It Works Section -- */}
      <section className="py-20">
        <div className="container mx-auto px-6">
          <h2 className="text-4xl font-bold text-center mb-12">
            Get Started in 3 Simple Steps
          </h2>
          <div className="max-w-3xl mx-auto grid md:grid-cols-1 gap-12">
            <HowItWorksStep number="1" title="Connect Your Accounts">
              Securely link your eBay, Facebook, and other marketplace accounts
              in seconds.
            </HowItWorksStep>
            <HowItWorksStep number="2" title="Create Your Listing">
              Write your ad description, set the price, and upload your photos
              just once.
            </HowItWorksStep>
            <HowItWorksStep number="3" title="Post Everywhere">
              Select where you want to post and hit 'Publish'. We handle the
              rest.
            </HowItWorksStep>
          </div>
        </div>
      </section>

      {/* --- Features Section -- */}
      <section className="py-20 bg-gray-800">
        <div className="container mx-auto px-6">
          <h2 className="text-4xl font-bold text-center mb-12">
            Your All-in-One Command Center
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <Feature title="Unified Dashboard">
              Manage all your listings, from every platform, in one clean
              interface. No more tab-switching chaos.
            </Feature>
            <Feature title="Performance Analytics">
              See which platforms are getting you the most views and leads, so
              you can optimize your strategy.
            </Feature>
            <Feature title="AI-Powered Descriptions">
              Stuck on what to write? Our AI assistant helps you craft
              compelling ad descriptions that sell.
            </Feature>
          </div>
        </div>
      </section>

      {/* --- Testimonial Section -- */}
      <section className="py-20">
        <div className="container mx-auto px-6 text-center max-w-3xl">
          <p className="text-2xl md:text-3xl font-serif italic text-gray-300">
            "CrossPostMe saved me at least 10 hours a week. I can't imagine
            going back to posting manually. It's an absolute game-changer for my
            resale business."
          </p>
          <p className="mt-6 text-lg font-semibold">- Sarah J, Power Seller</p>
        </div>
      </section>

      {/* --- Final CTA Section -- */}
      <section
        id="download"
        className="py-20 bg-gradient-to-t from-gray-900 to-gray-800"
      >
        <div className="container mx-auto px-6 text-center">
          <h2 className="text-4xl font-bold mb-4">
            Ready to Supercharge Your Sales?
          </h2>
          <p className="text-xl text-gray-400 mb-8">
            Get started for free. No credit card required.
          </p>
          <div className="flex justify-center space-x-4">
            <a
              href="#"
              className="bg-black text-white px-6 py-3 rounded-lg flex items-center space-x-2 border border-gray-600 hover:border-white transition"
            >
              <img
                src="https://upload.wikimedia.org/wikipedia/commons/3/3c/Download_on_the_App_Store_Badge.svg"
                alt="App Store"
                className="h-10"
              />
            </a>
            <a
              href="#"
              className="bg-black text-white px-6 py-3 rounded-lg flex items-center space-x-2 border border-gray-600 hover:border-white transition"
            >
              <img
                src="https://upload.wikimedia.org/wikipedia/commons/7/78/Google_Play_Store_badge_EN.svg"
                alt="Google Play"
                className="h-10"
              />
            </a>
          </div>
        </div>
      </section>

      {/* --- Footer -- */}
      <footer className="py-10 border-t border-gray-800">
        <div className="container mx-auto px-6 text-center text-gray-500">
          <p>&copy; 2024 CrossPostMe. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
