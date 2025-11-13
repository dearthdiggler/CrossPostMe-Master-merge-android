import React, { Suspense, lazy } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import { Toaster } from "./components/ui/toaster";

// Authentication
import Login, { AuthProvider, useAuth } from "./components/Login";

// Lazy load non-critical homepage sections for faster initial paint
const Hero = lazy(() => import("./components/Hero"));
const PublicDescription = lazy(() => import("./components/PublicDescription"));
const AISection = lazy(() => import("./components/AISection"));
const SpeedSection = lazy(() => import("./components/SpeedSection"));
const WhyChoose = lazy(() => import("./components/WhyChoose"));
const Services = lazy(() => import("./components/Services"));
const Pricing = lazy(() => import("./components/Pricing"));
const Company = lazy(() => import("./components/Company"));
const Comparison = lazy(() => import("./components/Comparison"));
const Benefits = lazy(() => import("./components/Benefits"));
const Testimonial = lazy(() => import("./components/Testimonial"));
const FAQ = lazy(() => import("./components/FAQ"));
const Blog = lazy(() => import("./components/Blog"));
const CTASection = lazy(() => import("./components/CTASection"));
const Footer = lazy(() => import("./components/Footer"));

// Lazy load marketplace pages
const Dashboard = lazy(() => import("./pages/Dashboard"));
const CreateAd = lazy(() => import("./pages/CreateAd"));
const EditAd = lazy(() => import("./pages/EditAd"));
const MyAds = lazy(() => import("./pages/MyAds"));
const Platforms = lazy(() => import("./pages/Platforms"));
const Analytics = lazy(() => import("./pages/Analytics"));
const LogoShowcase = lazy(() => import("./pages/LogoShowcase"));

// Simple loading fallback
const LoadingFallback = () => (
  <div className="min-h-screen flex items-center justify-center bg-white">
    <div className="text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
      <p className="text-gray-600">Loading...</p>
    </div>
  </div>
);

const Home = () => {
  return (
    <div className="min-h-screen bg-white">
      <Suspense fallback={<div style={{ height: "400px" }} />}>
        <Hero />
      </Suspense>
      <Suspense fallback={<div style={{ height: "400px" }} />}>
        <SpeedSection />
      </Suspense>
      <Suspense fallback={<div style={{ height: "400px" }} />}>
        <WhyChoose />
      </Suspense>
      <Suspense fallback={<div style={{ height: "400px" }} />}>
        <Services />
      </Suspense>
      <Suspense fallback={<div style={{ height: "400px" }} />}>
        <Pricing />
      </Suspense>
      <Suspense fallback={<div style={{ height: "400px" }} />}>
        <Comparison />
      </Suspense>
      <Suspense fallback={<div style={{ height: "400px" }} />}>
        <Benefits />
      </Suspense>
      <Suspense fallback={<div style={{ height: "400px" }} />}>
        <Testimonial />
      </Suspense>
      <Suspense fallback={<div style={{ height: "400px" }} />}>
        <FAQ />
      </Suspense>
      <Suspense fallback={<div style={{ height: "400px" }} />}>
        <Blog />
      </Suspense>
      <Suspense fallback={<div style={{ height: "400px" }} />}>
        <CTASection />
      </Suspense>
      <Suspense fallback={<div style={{ height: "400px" }} />}>
        <Footer />
      </Suspense>
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
          <Navbar />
          <Suspense fallback={<LoadingFallback />}>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Login mode="register" />} />
              <Route
                path="/pricing"
                element={
                  <Suspense fallback={<LoadingFallback />}>
                    <Pricing />
                  </Suspense>
                }
              />
              <Route
                path="/company"
                element={
                  <Suspense fallback={<LoadingFallback />}>
                    <Company />
                  </Suspense>
                }
              />
              <Route
                path="/marketplace/dashboard"
                element={
                  <ProtectedRoute>
                    <Suspense fallback={<LoadingFallback />}>
                      <Dashboard />
                    </Suspense>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/marketplace/create-ad"
                element={
                  <ProtectedRoute>
                    <Suspense fallback={<LoadingFallback />}>
                      <CreateAd />
                    </Suspense>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/marketplace/edit-ad/:id"
                element={
                  <ProtectedRoute>
                    <Suspense fallback={<LoadingFallback />}>
                      <EditAd />
                    </Suspense>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/marketplace/my-ads"
                element={
                  <ProtectedRoute>
                    <Suspense fallback={<LoadingFallback />}>
                      <MyAds />
                    </Suspense>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/marketplace/platforms"
                element={
                  <ProtectedRoute>
                    <Suspense fallback={<LoadingFallback />}>
                      <Platforms />
                    </Suspense>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/marketplace/analytics"
                element={
                  <ProtectedRoute>
                    <Suspense fallback={<LoadingFallback />}>
                      <Analytics />
                    </Suspense>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/logos"
                element={
                  <Suspense fallback={<LoadingFallback />}>
                    <LogoShowcase />
                  </Suspense>
                }
              />
            </Routes>
          </Suspense>
        </BrowserRouter>
        <Toaster />
      </div>
    </AuthProvider>
  );
}

export default App;
