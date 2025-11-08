import React from "react";
import { Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import PlatformConnections from "../components/PlatformConnections";

const Platforms = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center space-x-4 mb-8">
          <Link to="/marketplace/dashboard">
            <button className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors">
              <ArrowLeft className="w-4 h-4" />
              <span>Back to Dashboard</span>
            </button>
          </Link>
        </div>

        <PlatformConnections />
      </div>
    </div>
  );
};

export default Platforms;
