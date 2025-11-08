import React from "react";
import { Button } from "./ui/button";
import { CheckCircle, Clock, Users, TrendingUp } from "lucide-react";

const AISection = () => {
  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* AI Sales Team Section */}
        <div className="text-center mb-16">
          <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-6">
            Your Built-In AI Sales Team: Turning Leads Into Sales
          </h2>
          <p className="text-xl text-gray-600 max-w-4xl mx-auto">
            At CrossPostMe, we focus on practical automation that helps
            businesses manage listings and follow up with leads. Our{" "}
            <span className="font-semibold text-blue-600">
              Built-In AI Sales Team
            </span>{" "}
            feature assists with consistent lead follow-up and qualification.
          </p>
        </div>

        {/* What We Do */}
        <div className="bg-gradient-to-r from-blue-50 to-cyan-50 rounded-2xl p-8 md:p-12 mb-12">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">What We Do:</h3>
          <ul className="space-y-4">
            <li className="flex items-start space-x-3">
              <CheckCircle className="w-6 h-6 text-blue-600 flex-shrink-0 mt-1" />
              <span className="text-lg text-gray-700">
                Our <span className="font-semibold">Sales AI</span> can be
                configured to respond to incoming leads and assist with
                follow-up.
              </span>
            </li>
            <li className="flex items-start space-x-3">
              <CheckCircle className="w-6 h-6 text-blue-600 flex-shrink-0 mt-1" />
              <span className="text-lg text-gray-700">
                Provide configurable voice or text responses and professional
                follow-ups to keep potential customers engaged.
              </span>
            </li>
            <li className="flex items-start space-x-3">
              <CheckCircle className="w-6 h-6 text-blue-600 flex-shrink-0 mt-1" />
              <span className="text-lg text-gray-700">
                With CrossPostMe, you get an automated posting and follow-up
                tool that helps reduce manual work and improve response times.
              </span>
            </li>
          </ul>
        </div>

        {/* Why Businesses Love Section */}
        <div className="mb-16">
          <h3 className="text-3xl font-bold text-center text-gray-900 mb-12">
            Why Businesses Love Our Built-In Sales Team
          </h3>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Clock className="w-8 h-8 text-blue-600" />
              </div>
              <h4 className="text-xl font-bold text-gray-900 mb-3">
                Close Deals Faster
              </h4>
              <p className="text-gray-600">
                Every lead is responded to promptly, ensuring you never miss an
                opportunity to convert potential customers.
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Users className="w-8 h-8 text-green-600" />
              </div>
              <h4 className="text-xl font-bold text-gray-900 mb-3">
                Fill Staffing Gaps
              </h4>
              <p className="text-gray-600">
                Don't have the resources to handle incoming inquiries? We've got
                you covered with a sales team ready to step in.
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <TrendingUp className="w-8 h-8 text-purple-600" />
              </div>
              <h4 className="text-xl font-bold text-gray-900 mb-3">
                Maximize ROI
              </h4>
              <p className="text-gray-600">
                Our integrated approach of ad posting and lead follow-up means
                your investment works harder for you.
              </p>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="bg-gradient-to-r from-blue-600 to-cyan-500 rounded-2xl p-8 md:p-12 text-center text-white">
          <h3 className="text-3xl font-bold mb-4">
            From Lead to Follow-Up: Simplify Your Workflow
          </h3>
          <p className="text-xl mb-8 text-blue-100">
            CrossPostMe helps automate posting and lead follow-up so small teams
            can maintain consistency without additional headcount.
          </p>
          <Button className="bg-white text-blue-600 hover:bg-gray-100 font-semibold px-8 py-6 text-lg">
            Schedule Zoom Demo
          </Button>
        </div>

        {/* 24/7 Banner */}
        <div className="mt-20 text-center">
          <div className="inline-block bg-gradient-to-r from-blue-600 to-blue-700 text-white px-8 py-4 rounded-full text-xl font-bold shadow-lg">
            24/7 AI That Posts, Responds, and Books Appointments — So You Don't
            Have To
          </div>
        </div>
      </div>
    </section>
  );
};

export default AISection;
