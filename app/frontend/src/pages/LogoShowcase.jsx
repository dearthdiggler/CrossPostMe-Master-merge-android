import React from "react";
import {
  CrossPostMeLogo1,
  CrossPostMeLogo2,
  CrossPostMeLogo3,
  XPostMeLogo1,
  XPostMeLogo2,
  XPostMeLogo3,
} from "../components/LogoVariations";

// Reusable component for logo options
const LogoOption = ({ title, description, LogoComponent, bestFor }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-8 mb-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold mb-2">{title}</h3>
          <p className="text-gray-600">{description}</p>
        </div>
      </div>
      <div className="flex gap-8 items-center flex-wrap">
        <div className="bg-white p-4 rounded">
          <LogoComponent size="small" />
        </div>
        <div className="bg-white p-4 rounded">
          <LogoComponent size="default" />
        </div>
        <div className="bg-white p-4 rounded">
          <LogoComponent size="large" />
        </div>
      </div>
      <div className="mt-4 flex gap-4">
        <div className="bg-gray-900 p-4 rounded flex-1">
          <LogoComponent size="default" />
        </div>
        <div className="bg-blue-600 p-4 rounded flex-1">
          <LogoComponent size="default" />
        </div>
      </div>
      <div className="mt-4 text-sm text-gray-600">
        <strong>Best for:</strong> {bestFor}
      </div>
    </div>
  );
};

const LogoShowcase = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-4">
          Logo Design Options
        </h1>
        <p className="text-center text-gray-600 mb-12">
          Choose your favorite design to represent your brand
        </p>

        {/* CrossPostMe Options */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold mb-8 text-gray-800">
            CrossPostMe Options
          </h2>

          <LogoOption
            title="Option 1: Geometric Cross"
            description="Modern, clean design with gradient plus symbol. Professional and tech-forward."
            LogoComponent={CrossPostMeLogo1}
            bestFor="Professional SaaS feel, corporate clients, B2B marketplace"
          />

          <LogoOption
            title="Option 2: Arrow Network"
            description="Four arrows radiating from center. Shows distribution and multi-platform reach."
            LogoComponent={CrossPostMeLogo2}
            bestFor="Emphasizing distribution, showing action and movement, tech-savvy users"
          />

          <LogoOption
            title="Option 3: Overlapping Circles (Network Effect)"
            description="Four platforms merging into one. Shows connectivity and unity."
            LogoComponent={CrossPostMeLogo3}
            bestFor="Community feel, network effects, social marketplace emphasis"
          />
        </section>

        {/* XPostMe Options */}
        <section>
          <h2 className="text-3xl font-bold mb-8 text-gray-800">
            XPostMe Options
          </h2>

          <LogoOption
            title="Option 1: Modern X with Gradient"
            description="Bold X symbol with vibrant multi-color gradient. Eye-catching and energetic."
            LogoComponent={XPostMeLogo1}
            bestFor="Consumer-focused, young demographic, casual sellers"
          />

          <LogoOption
            title="Option 2: Minimalist Bold X"
            description="Strong, simple X in a rotated square. Premium and confident."
            LogoComponent={XPostMeLogo2}
            bestFor="Premium positioning, power users, app-style branding"
          />

          <LogoOption
            title="Option 3: Connected Nodes"
            description="Network visualization with connected points forming X. Shows interconnectivity."
            LogoComponent={XPostMeLogo3}
            bestFor="Tech-forward positioning, API/platform play, developer audience"
          />
        </section>

        {/* Recommendation Section */}
        <section className="mt-16 bg-blue-50 rounded-lg p-8">
          <h2 className="text-2xl font-bold mb-4">Branding Recommendation</h2>

          <div className="grid md:grid-cols-2 gap-8 mb-8">
            <div>
              <h3 className="text-xl font-bold mb-3 text-blue-600">
                CrossPostMe
              </h3>
              <div className="space-y-2 text-sm">
                <p>
                  <strong>✅ Pros:</strong>
                </p>
                <ul className="list-disc ml-5 space-y-1">
                  <li>Immediately clear what the service does</li>
                  <li>Professional and trustworthy</li>
                  <li>Better for SEO (includes "post" keyword)</li>
                  <li>Easy to pronounce and spell</li>
                  <li>Friendly, accessible tone</li>
                </ul>
                <p className="mt-3">
                  <strong>⚠️ Cons:</strong>
                </p>
                <ul className="list-disc ml-5 space-y-1">
                  <li>Longer to type and remember</li>
                  <li>Domain might be more expensive</li>
                  <li>Less "tech" feel</li>
                </ul>
                <p className="mt-3">
                  <strong>Best for:</strong> Mainstream marketplace sellers,
                  mom-and-pop shops, casual users
                </p>
              </div>
            </div>

            <div>
              <h3 className="text-xl font-bold mb-3 text-purple-600">
                XPostMe
              </h3>
              <div className="space-y-2 text-sm">
                <p>
                  <strong>✅ Pros:</strong>
                </p>
                <ul className="list-disc ml-5 space-y-1">
                  <li>Shorter, punchier, more memorable</li>
                  <li>Modern "X" branding (like SpaceX, X.com)</li>
                  <li>Easier to type and hashtag (#xpostme)</li>
                  <li>Tech-forward, innovative feel</li>
                  <li>Could trademark more easily</li>
                </ul>
                <p className="mt-3">
                  <strong>⚠️ Cons:</strong>
                </p>
                <ul className="list-disc ml-5 space-y-1">
                  <li>May need explanation ("Is it 'ex' or 'cross'?")</li>
                  <li>Could be confused verbally</li>
                  <li>Less obvious functionality</li>
                </ul>
                <p className="mt-3">
                  <strong>Best for:</strong> Power sellers, resellers,
                  tech-savvy users, viral growth potential
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded p-6">
            <h3 className="text-lg font-bold mb-2">
              🎯 My Recommendation:{" "}
              <span className="text-blue-600">CrossPostMe</span>
            </h3>
            <p className="text-gray-700 mb-4">
              For a marketplace cross-posting tool targeting everyday sellers
              (your primary audience),
              <strong> CrossPostMe</strong> is the stronger choice. It's
              immediately understandable, SEO-friendly, and builds trust. The
              name communicates the value proposition instantly.
            </p>
            <p className="text-gray-700 mb-4">
              <strong>However</strong>, if you plan to pivot toward power users,
              API access, or want to position as a tech platform,{" "}
              <strong>XPostMe</strong> has better brand potential and viral
              marketing appeal.
            </p>
            <p className="text-gray-700 font-semibold">
              Suggested compromise: Launch as <strong>CrossPostMe</strong>{" "}
              (clear value prop), but secure xpostme.com and use it as a short
              URL redirect. Best of both worlds!
            </p>
          </div>

          <div className="mt-6 bg-yellow-50 border-l-4 border-yellow-400 p-4">
            <p className="text-sm text-yellow-800">
              <strong>Domain Check:</strong> Before finalizing, verify domain
              availability for both options. Also check social media handles
              (@crosspostme vs @xpostme) across platforms.
            </p>
          </div>
        </section>
      </div>
    </div>
  );
};

export default LogoShowcase;
