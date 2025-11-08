import React from "react";

const Company = () => {
  return (
    <section className="min-h-screen bg-white py-20">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold">About CrossPostMe</h1>
          <p className="mt-4 text-lg text-gray-600">
            We help sellers post to multiple marketplaces with one click.
            Founded to make selling easier and faster.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          <div>
            <h3 className="text-2xl font-semibold mb-3">Our Mission</h3>
            <p className="text-gray-700">
              Make online selling efficient by automating cross-posting and
              centralizing messaging so sellers spend less time managing
              listings and more time selling.
            </p>
          </div>

          <div>
            <h3 className="text-2xl font-semibold mb-3">Leadership</h3>
            <p className="text-gray-700">
              Led by experienced marketplace operators and engineers,
              CrossPostMe focuses on robust integrations and reliable posting.
            </p>
          </div>
        </div>

        <div className="mt-12 text-center">
          <a
            href="/pricing"
            className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-3 rounded"
          >
            See Pricing
          </a>
        </div>
      </div>
    </section>
  );
};

export default Company;
