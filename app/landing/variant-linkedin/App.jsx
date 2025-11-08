import React from "react";

// --- Icon Components ---
const FeatureIcon = ({ path }) => (
  <svg
    className="h-8 w-8 text-blue-600 mb-4"
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    viewBox="0 0 24 24"
    stroke="currentColor"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d={path}
    />
  </svg>
);

function App() {
  return (
    <div className="bg-gray-50 font-sans">
      {/* --- Header -- */}
      <header className="bg-white border-b border-gray-200">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <div className="text-2xl font-bold text-gray-800 tracking-wider">
            CrossPostMe
          </div>
          <nav className="space-x-6 flex items-center">
            <a
              href="http://localhost:3000/login"
              className="text-gray-600 hover:text-gray-900 transition-colors font-medium"
            >
              Log In
            </a>
            <a
              href="http://localhost:3000/register"
              className="bg-blue-600 text-white px-5 py-2.5 rounded-lg font-semibold hover:bg-blue-700 transition-all"
            >
              Start Free Trial
            </a>
          </nav>
        </div>
      </header>

      {/* --- Hero Section -- */}
      <main className="text-center py-20 md:py-32">
        <div className="container mx-auto px-6">
          <h1 className="text-3xl md:text-5xl font-extrabold text-gray-900 leading-tight mb-4">
            The Efficiency Platform for Online Sellers
          </h1>
          <p className="text-lg md:text-xl text-gray-600 mb-10 max-w-3xl mx-auto">
            Automate your listings, track performance, and save dozens of hours
            every week. Focus on selling, not on tedious administrative tasks.
          </p>
          <a
            href="http://localhost:3000/register"
            className="bg-blue-600 text-white px-10 py-4 rounded-lg font-bold text-lg hover:bg-blue-700 transition-transform hover:scale-105 inline-block"
          >
            Start Your 14-Day Free Trial
          </a>
        </div>
      </main>

      {/* --- Trusted By Section -- */}
      <div className="pb-20">
        <div className="container mx-auto px-6">
          <p className="text-center text-sm font-semibold text-gray-500 uppercase tracking-wider">
            TRUSTED BY TOP RESELLERS & SMALL BUSINESSES
          </p>
          {/* Placeholder for logos */}
          <div className="flex justify-center items-center mt-6 space-x-8 md:space-x-12 text-gray-400">
            <p className="font-bold text-lg">VINTAGE FINDS</p>
            <p className="font-bold text-lg">SNEAKER SOURCE</p>
            <p className="font-bold text-lg">RETRO REVIVAL</p>
            <p className="font-bold text-lg">GADGET HUB</p>
          </div>
        </div>
      </div>

      {/* --- Features Section -- */}
      <section className="py-20 bg-white border-t border-b">
        <div className="container mx-auto px-6">
          <h2 className="text-4xl font-bold text-center text-gray-900 mb-16">
            A Better Way to Manage Your Online Store
          </h2>
          <div className="grid md:grid-cols-3 gap-10 max-w-6xl mx-auto">
            <div className="text-center">
              <FeatureIcon path="M13 10V3L4 14h7v7l9-11h-7z" />
              <h3 className="text-xl font-bold text-gray-800 mb-2">
                One-Click Cross-Posting
              </h3>
              <p className="text-gray-600">
                Publish your listings to eBay, Facebook Marketplace, and more
                with a single click. No more copy-pasting.
              </p>
            </div>
            <div className="text-center">
              <FeatureIcon path="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              <h3 className="text-xl font-bold text-gray-800 mb-2">
                Unified Analytics
              </h3>
              <p className="text-gray-600">
                Track views, messages, and sales across all platforms from one
                dashboard. Make data-driven decisions.
              </p>
            </div>
            <div className="text-center">
              <FeatureIcon path="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              <h3 className="text-xl font-bold text-gray-800 mb-2">
                Smart Scheduling
              </h3>
              <p className="text-gray-600">
                Schedule your posts to go live at peak times for maximum
                visibility and engagement.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* --- Testimonial Section -- */}
      <section className="py-20">
        <div className="container mx-auto px-6 text-center max-w-3xl">
          <img
            className="w-24 h-24 rounded-full mx-auto mb-6"
            src="https://randomuser.me/api/portraits/women/44.jpg"
            alt="Testimonial author"
          />
          <p className="text-xl md:text-2xl text-gray-700">
            "CrossPostMe is an indispensable part of our workflow. It has freed
            up at least 10-15 hours per week, allowing us to focus on sourcing
            and customer service. Our sales have increased 30% since we started
            using it."
          </p>
          <p className="mt-6 font-bold text-gray-900">- Emily Carter</p>
          <p className="text-sm text-gray-600">Owner, Retro Revival</p>
        </div>
      </section>

      {/* --- Footer -- */}
      <footer className="bg-white border-t py-10">
        <div className="container mx-auto px-6 text-center text-gray-500">
          <p>&copy; 2024 CrossPostMe. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
