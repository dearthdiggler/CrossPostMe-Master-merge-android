import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ChevronDown, Phone, Menu, X, User, LogOut } from "lucide-react";
import { Button } from "./ui/button";
import { useAuth } from "./Login";
import Logo from "./Logo";

const Navbar = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const navItems = [
    {
      label: "Marketplace Platforms",
      hasDropdown: true,
      items: ["OfferUp", "Craigslist", "Facebook Marketplace", "eBay"],
    },
    {
      label: "Features",
      hasDropdown: true,
      items: [
        "Auto-Posting",
        "Multi-Platform Sync",
        "Analytics Dashboard",
        "Message Management",
      ],
    },
    {
      label: "Company",
      hasDropdown: false,
      items: [],
    },
    {
      label: "Pricing",
      hasDropdown: false,
      items: [],
    },
    // Dormant: AI Lead Gen and Outsourcing Services removed
  ];

  return (
    <nav className="bg-white shadow-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-20">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3">
            <Logo size="default" />
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden lg:flex items-center space-x-8">
            {navItems.map((item, index) => (
              <div key={index} className="relative group">
                {item.hasDropdown ? (
                  <button className="flex items-center space-x-1 text-gray-700 hover:text-blue-600 font-medium transition-colors">
                    <span>{item.label}</span>
                    <ChevronDown className="w-4 h-4" />
                  </button>
                ) : (
                  <Link
                    to={
                      item.label === "Pricing"
                        ? "/pricing"
                        : item.label === "Company"
                          ? "/company"
                          : "#"
                    }
                    className="flex items-center space-x-1 text-gray-700 hover:text-blue-600 font-medium transition-colors"
                  >
                    <span>{item.label}</span>
                  </Link>
                )}
                {item.hasDropdown && (
                  <div className="absolute top-full left-0 mt-2 w-56 bg-white rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                    <div className="py-2">
                      {item.items.map((subItem, subIndex) => {
                        // Map sub-items to their proper URLs
                        const getItemUrl = (itemName) => {
                          const urlMap = {
                            OfferUp: "/marketplace/platforms",
                            Craigslist: "/marketplace/platforms",
                            "Facebook Marketplace": "/marketplace/platforms",
                            eBay: "/marketplace/platforms",
                            "Auto-Posting": "/marketplace/create-ad",
                            "Multi-Platform Sync": "/marketplace/platforms",
                            "Analytics Dashboard": "/marketplace/analytics",
                            "Message Management": "/marketplace/dashboard",
                          };
                          return urlMap[itemName] || "#";
                        };

                        return (
                          <Link
                            key={subIndex}
                            to={getItemUrl(subItem)}
                            className="block px-4 py-2 text-gray-700 hover:bg-blue-50 hover:text-blue-600 transition-colors"
                          >
                            {subItem}
                          </Link>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* CTA Buttons */}
          <div className="hidden lg:flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <Link to="/marketplace/dashboard">
                  <Button variant="outline" className="font-semibold px-6">
                    Dashboard
                  </Button>
                </Link>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">
                    <User className="w-4 h-4 inline mr-1" />
                    {user?.username}
                  </span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      logout();
                      navigate("/");
                    }}
                    className="text-gray-600 hover:text-red-600"
                    data-testid="logout-button"
                    aria-label="Log Out"
                  >
                    <LogOut className="w-4 h-4" />
                  </Button>
                </div>
              </>
            ) : (
              <>
                <Link to="/login">
                  <Button variant="outline" className="font-semibold px-6">
                    Login
                  </Button>
                </Link>
                <Button
                  className="bg-yellow-500 hover:bg-yellow-600 text-black font-semibold px-6"
                  onClick={() => window.open("tel:623-777-9969", "_self")}
                >
                  Book Demo
                </Button>
              </>
            )}
            <Button
              className="bg-blue-500 hover:bg-blue-600 text-white font-semibold px-6"
              onClick={() => window.open("tel:623-777-9969", "_self")}
            >
              <Phone className="w-4 h-4 mr-2" />
              623-777-9969
            </Button>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="lg:hidden p-2 rounded-lg hover:bg-gray-100"
          >
            {mobileMenuOpen ? (
              <X className="w-6 h-6" />
            ) : (
              <Menu className="w-6 h-6" />
            )}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="lg:hidden bg-white border-t">
          <div className="px-4 py-4 space-y-4">
            {navItems.map((item, index) => (
              <div key={index}>
                {item.hasDropdown ? (
                  <button className="w-full text-left font-medium text-gray-700 py-2">
                    {item.label}
                  </button>
                ) : (
                  <Link
                    to={
                      item.label === "Pricing"
                        ? "/pricing"
                        : item.label === "Company"
                          ? "/company"
                          : "#"
                    }
                    onClick={() => setMobileMenuOpen(false)}
                    className="w-full block py-2 text-gray-700 font-medium"
                  >
                    {item.label}
                  </Link>
                )}
              </div>
            ))}
            <div className="space-y-2 pt-4 border-t">
              {isAuthenticated ? (
                <>
                  <Link to="/marketplace/dashboard">
                    <Button className="w-full bg-blue-500 hover:bg-blue-600 text-white font-semibold">
                      Dashboard
                    </Button>
                  </Link>
                  <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <span className="text-sm text-gray-600">
                      <User className="w-4 h-4 inline mr-1" />
                      {user?.username}
                    </span>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        logout();
                        navigate("/");
                        setMobileMenuOpen(false);
                      }}
                      className="text-red-600 hover:text-red-700"
                      data-testid="logout-button-mobile"
                      aria-label="Log Out"
                    >
                      <LogOut className="w-4 h-4" />
                    </Button>
                  </div>
                </>
              ) : (
                <>
                  <Link to="/login">
                    <Button className="w-full bg-blue-500 hover:bg-blue-600 text-white font-semibold">
                      Login
                    </Button>
                  </Link>
                  <Button
                    className="w-full bg-yellow-500 hover:bg-yellow-600 text-black font-semibold"
                    onClick={() => window.open("tel:623-777-9969", "_self")}
                  >
                    Book Demo
                  </Button>
                </>
              )}
              <Button
                className="w-full bg-gray-500 hover:bg-gray-600 text-white font-semibold"
                onClick={() => window.open("tel:623-777-9969", "_self")}
              >
                <Phone className="w-4 h-4 mr-2" />
                623-777-9969
              </Button>
            </div>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
