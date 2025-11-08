import React from "react";
import { Link } from "react-router-dom";
import { Facebook, Twitter, Linkedin, Mail, Phone, MapPin } from "lucide-react";
import Logo from "./Logo";

const Footer = () => {
  const footerLinks = {
    Services: [
      "AI Marketplace Listings",
      "Google Maps SEO",
      "Lead Generation",
      "Account Restoration",
      "Real Estate Solutions",
    ],
    Company: ["About Us", "Blog", "Case Studies", "Testimonials", "Contact"],
    Resources: [
      "Help Center",
      "API Documentation",
      "Community",
      "Partners",
      "Pricing",
    ],
    Legal: [
      "Privacy Policy",
      "Terms of Service",
      "Cookie Policy",
      "GDPR",
      "Accessibility",
    ],
  };

  return (
    <footer className="bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid md:grid-cols-2 lg:grid-cols-6 gap-8 mb-12">
          {/* Brand Column */}
          <div className="lg:col-span-2">
            <Link to="/" className="flex items-center space-x-3 mb-6">
              <Logo size="default" />
            </Link>
            <p className="text-gray-400 mb-6 leading-relaxed">
              Automated multi-platform posting and lead follow-up to keep your
              listings working for you around the clock.
            </p>
            <div className="flex space-x-4">
              <a
                href="https://facebook.com/crosspostme"
                target="_blank"
                rel="noopener noreferrer"
                className="w-10 h-10 bg-gray-800 rounded-full flex items-center justify-center hover:bg-blue-600 transition-colors"
                title="Connect on Facebook"
              >
                <Facebook className="w-5 h-5" />
              </a>
              <a
                href="https://twitter.com/crosspostme"
                target="_blank"
                rel="noopener noreferrer"
                className="w-10 h-10 bg-gray-800 rounded-full flex items-center justify-center hover:bg-blue-600 transition-colors"
                title="Follow on Twitter"
              >
                <Twitter className="w-5 h-5" />
              </a>
              <a
                href="https://linkedin.com/company/crosspostme"
                target="_blank"
                rel="noopener noreferrer"
                className="w-10 h-10 bg-gray-800 rounded-full flex items-center justify-center hover:bg-blue-600 transition-colors"
                title="Connect on LinkedIn"
              >
                <Linkedin className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Links Columns */}
          {Object.entries(footerLinks).map(([category, links]) => (
            <div key={category}>
              <h3 className="font-bold text-lg mb-4">{category}</h3>
              <ul className="space-y-2">
                {links.map((link, index) => (
                  <li key={index}>
                    <Link
                      to="#"
                      className="text-gray-400 hover:text-white transition-colors"
                    >
                      {link}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Contact Info */}
        <div className="border-t border-gray-800 pt-8 mb-8">
          <div className="grid md:grid-cols-3 gap-6">
            <div className="flex items-start space-x-3">
              <Phone className="w-5 h-5 text-blue-500 flex-shrink-0 mt-1" />
              <div>
                <p className="font-semibold mb-1">Phone</p>
                <a
                  href="tel:623-777-9969"
                  className="text-gray-400 hover:text-white"
                >
                  623-777-9969
                </a>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <Mail className="w-5 h-5 text-blue-500 flex-shrink-0 mt-1" />
              <div>
                <p className="font-semibold mb-1">Email</p>
                <a
                  href="mailto:crosspostme@gmail.com"
                  className="text-gray-400 hover:text-white"
                >
                  crosspostme@gmail.com
                </a>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <MapPin className="w-5 h-5 text-blue-500 flex-shrink-0 mt-1" />
              <div>
                <p className="font-semibold mb-1">Location</p>
                <p className="text-gray-400">United States</p>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-gray-800 pt-8 text-center text-gray-400">
          <p>
            &copy; {new Date().getFullYear()} CrossPostMe. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
