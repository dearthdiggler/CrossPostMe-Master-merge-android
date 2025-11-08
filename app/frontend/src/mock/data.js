// Mock data for CrossPostMe.com

export const services = [
  {
    id: 1,
    title: "OfferUp Auto-Posting",
    description:
      "Post your items to OfferUp automatically with optimized titles, descriptions, and pricing. Track views and messages in one dashboard.",
    link: "/services/offerup-posting",
    colorScheme: "blue",
  },
  {
    id: 2,
    title: "Craigslist Multi-City Posting",
    description:
      "Reach buyers across multiple cities and categories on Craigslist. Our system rotates IPs and varies content to avoid flags while maximizing visibility.",
    link: "/services/craigslist-posting",
    colorScheme: "gray",
  },
  {
    id: 3,
    title: "Facebook Marketplace Sync",
    description:
      "List your items on Facebook Marketplace with automatic posting, renewal, and message management. Reach local buyers where they shop most.",
    link: "/services/facebook-marketplace",
    colorScheme: "gray",
  },
  {
    id: 4,
    title: "eBay Listing Management",
    description:
      "Create and manage eBay auctions and fixed-price listings. Sync inventory, track bids, and handle buyer communications automatically.",
    link: "/services/ebay-management",
    colorScheme: "blue",
  },
  {
    id: 5,
    title: "Cross-Platform Analytics",
    description:
      "See performance across all marketplaces in one dashboard. Track views, messages, and sales to optimize your listings.",
    link: "/services/analytics",
    colorScheme: "gray",
  },
  {
    id: 6,
    title: "AI-Powered Descriptions",
    description:
      "Generate compelling item descriptions and titles automatically. Our AI adapts your content for each platform's best practices.",
    link: "/services/ai-descriptions",
    colorScheme: "blue",
  },
  {
    id: 7,
    title: "Automated Message Responses",
    description:
      "Never miss a buyer inquiry. Set up auto-responses for common questions and get notified of important messages instantly.",
    link: "/services/auto-responses",
    colorScheme: "gray",
  },
  {
    id: 8,
    title: "Inventory Management",
    description:
      "Track your items across all platforms. Mark as sold on one marketplace and automatically remove from others to prevent overselling.",
    link: "/services/inventory",
    colorScheme: "blue",
  },
];

export const pricingPlans = [
  {
    id: 1,
    name: "Starter",
    price: 29,
    period: "month",
    description: "Perfect for casual sellers",
    features: [
      "Post to all 4 platforms (OfferUp, Craigslist, Facebook, eBay)",
      "Up to 25 active listings",
      "AI-powered descriptions and titles",
      "Basic analytics dashboard",
      "Email support",
      "Mobile app access",
      "Automatic listing renewals",
      "Single user account",
    ],
    popular: false,
  },
  {
    id: 2,
    name: "Professional",
    price: 79,
    period: "month",
    description: "For active sellers",
    features: [
      "Everything in Starter +",
      "Up to 100 active listings",
      "Multi-city Craigslist posting",
      "Automated message responses",
      "Inventory sync across platforms",
      "Priority email & chat support",
      "Bulk upload & editing",
      "Team collaboration (3 users)",
      "Advanced analytics & insights",
    ],
    popular: true,
  },
  {
    id: 3,
    name: "Business",
    price: "Custom",
    period: "",
    description: "For high-volume sellers",
    features: [
      "Everything in Professional +",
      "Unlimited listings",
      "Dedicated account manager",
      "Custom automation workflows",
      "API access for integrations",
      "White-label options available",
      "Phone & priority support",
      "Unlimited team members",
      "Custom reporting",
      "SLA guarantees",
    ],
    popular: false,
  },
];

export const benefits = [
  {
    id: 1,
    title: "Save Hours Every Week",
    description:
      "Stop manually posting to each marketplace. CrossPostMe automates the entire process, freeing up your time to source more inventory or grow your business.",
  },
  {
    id: 2,
    title: "Reach More Buyers",
    description:
      "Your items get seen by millions of shoppers across OfferUp, Craigslist, Facebook Marketplace, and eBay simultaneously.",
  },
  {
    id: 3,
    title: "Sell Faster",
    description:
      "More visibility means more inquiries and faster sales. Items posted to multiple platforms sell significantly faster than single-platform listings.",
  },
  {
    id: 4,
    title: "Never Miss a Message",
    description:
      "Manage all buyer messages from every platform in one unified inbox. Set up auto-responses to engage buyers instantly, even when you're busy.",
  },
  {
    id: 5,
    title: "Prevent Overselling",
    description:
      "When an item sells on one platform, CrossPostMe automatically removes it from all other marketplaces to prevent awkward buyer situations.",
  },
  {
    id: 6,
    title: "Optimize for Each Platform",
    description:
      "Our AI tailors your listings for each marketplace's algorithm and buyer behavior, maximizing your visibility and sales potential.",
  },
];

export const faqs = [
  {
    id: 1,
    question: "Which marketplaces does CrossPostMe support?",
    answer:
      "CrossPostMe currently supports the four major marketplaces: OfferUp, Craigslist, Facebook Marketplace, and eBay. We're working on adding Etsy, Poshmark, and other platforms in future updates.",
  },
  {
    id: 2,
    question: "Is there a contract or commitment?",
    answer:
      "No contracts required. You can cancel anytime. We offer month-to-month plans so you only continue if you're seeing results.",
  },
  {
    id: 3,
    question: "How do I connect my marketplace accounts?",
    answer:
      "During onboarding, you'll securely connect your existing accounts for each marketplace. We use secure OAuth connections where available and guide you through the setup process for each platform.",
  },
  {
    id: 4,
    question: "Will my accounts get flagged or banned?",
    answer:
      "CrossPostMe follows each platform's terms of service and uses smart posting patterns to avoid flags. We rotate IPs, vary content, and respect posting limits to keep your accounts safe.",
  },
  {
    id: 5,
    question: "Can I customize my listings for each platform?",
    answer:
      "Absolutely! While our AI generates optimized listings for each platform, you have full control to edit titles, descriptions, pricing, and photos. You can also set platform-specific rules and preferences.",
  },
  {
    id: 6,
    question: "How does the message management work?",
    answer:
      "All buyer messages from every platform come into one unified inbox in your CrossPostMe dashboard. You can set up auto-responses for common questions and get notifications for important messages.",
  },
];

export const blogPosts = [
  {
    id: 1,
    title: "The Local Delivery Promise That Wins Appliance Quotes",
    category: "Marketing Tips",
    image: "/api/placeholder/400/250",
    link: "/blog/local-delivery-promise",
  },
  {
    id: 2,
    title: "5 Retargeting Angles for Container Mods & Offices",
    category: "Case Studies",
    image: "/api/placeholder/400/250",
    link: "/blog/retargeting-angles",
  },
  {
    id: 3,
    title: "Boost Your Jewelry Sales with One Simple Google Maps Tweak",
    category: "SEO Tips",
    image: "/api/placeholder/400/250",
    link: "/blog/google-maps-tweak",
  },
];

export const testimonials = [
  {
    id: 1,
    name: "Jessica T.",
    role: "Small Business Owner",
    content:
      "CrossPostMe helped me grow my customer base without breaking the bank. The automation tools saved significant time and drove more inquiries.",
    rating: 5,
  },
  {
    id: 2,
    name: "Michael R.",
    role: "Real Estate Agent",
    content:
      "Reported significant inquiry growth from marketplace postings and improved conversion after using CrossPostMe's tools.",
    rating: 5,
  },
];

export const comparisonData = [
  {
    feature: "Cost per Lead",
    crossPostMe: "$1-$5",
    traditionalAds: "$15-$50",
  },
  {
    feature: "Engagement",
    crossPostMe: "70% higher",
    traditionalAds: "Lower without boosting",
  },
  {
    feature: "Lead Conversion Rate",
    crossPostMe: "2x higher",
    traditionalAds: "Lower, less engaged leads",
  },
  {
    feature: "Ad Lifespan",
    crossPostMe: "3-4 weeks",
    traditionalAds: "Ends when budget ends",
  },
  {
    feature: "Automation",
    crossPostMe: "Yes",
    traditionalAds: "No",
  },
  {
    feature: "Trust Level",
    crossPostMe: "High (non-sponsored)",
    traditionalAds: "Low (sponsored tag)",
  },
];
