import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import PublicDescription from "./components/PublicDescription";
import AISection from "./components/AISection";
import SpeedSection from "./components/SpeedSection";
import WhyChoose from "./components/WhyChoose";
import Services from "./components/Services";
import Pricing from "./components/Pricing";
import Company from "./components/Company";
import Comparison from "./components/Comparison";
import Benefits from "./components/Benefits";
import Testimonial from "./components/Testimonial";
import FAQ from "./components/FAQ";
import Blog from "./components/Blog";
import CTASection from "./components/CTASection";
import Footer from "./components/Footer";
import { Toaster } from "./components/ui/toaster";

// Authentication
import Login, { AuthProvider, useAuth } from "./components/Login";

// Marketplace Pages
import Dashboard from "./pages/Dashboard";
import CreateAd from "./pages/CreateAd";
import EditAd from "./pages/EditAd";
import MyAds from "./pages/MyAds";
import Platforms from "./pages/Platforms";
import Analytics from "./pages/Analytics";
import LogoShowcase from "./pages/LogoShowcase";

const Home = () => {
  // Public homepage: always show full marketing content so visitors
  // can see hero, pricing, company info, etc. Authentication only
  // gates marketplace routes.
  return (
    <div className="min-h-screen bg-white">
      <Hero />
      {/* <AISection /> - Dormant: AI Lead Gen */}
      <SpeedSection />
      <WhyChoose />
      <Services />
      <Pricing />
      <Comparison />
      <Benefits />
      <Testimonial />
      <FAQ />
      <Blog />
      <CTASection />
      <Footer />
    </div>
  );
};

// Protected Route wrapper for marketplace pages
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Login />;
  }

  return children;
};

function App() {
  return (
    <AuthProvider>
      <div className="App">
        <BrowserRouter>
          {/* Navbar is intentionally rendered outside route-level guards so it's
              always visible to all visitors (unauthenticated or not). */}
          <Navbar />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Login mode="register" />} />
            <Route path="/pricing" element={<Pricing />} />
            <Route path="/company" element={<Company />} />
            <Route
              path="/marketplace/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/marketplace/create-ad"
              element={
                <ProtectedRoute>
                  <CreateAd />
                </ProtectedRoute>
              }
            />
            <Route
              path="/marketplace/edit-ad/:id"
              element={
                <ProtectedRoute>
                  <EditAd />
                </ProtectedRoute>
              }
            />
            <Route
              path="/marketplace/my-ads"
              element={
                <ProtectedRoute>
                  <MyAds />
                </ProtectedRoute>
              }
            />
            <Route
              path="/marketplace/platforms"
              element={
                <ProtectedRoute>
                  <Platforms />
                </ProtectedRoute>
              }
            />
            <Route
              path="/marketplace/analytics"
              element={
                <ProtectedRoute>
                  <Analytics />
                </ProtectedRoute>
              }
            />
            <Route path="/logos" element={<LogoShowcase />} />
          </Routes>
        </BrowserRouter>
        <Toaster />
      </div>
    </AuthProvider>
  );
}

export default App;
