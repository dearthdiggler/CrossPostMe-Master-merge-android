import React from "react";
import { services } from "../mock/data";
import { Button } from "./ui/button";
import { ArrowRight } from "lucide-react";

const Services = () => {
  return (
    <section className="py-20 bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-5xl font-bold text-white mb-4">
            AI-POWERED <span className="text-blue-500">SERVICES</span>
          </h2>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {services.map((service, index) => (
            <div
              key={service.id}
              className={`rounded-2xl p-8 transition-all duration-300 hover:scale-105 ${
                service.colorScheme === "blue"
                  ? "bg-gradient-to-br from-blue-600 to-blue-700 text-white"
                  : "bg-gray-100 text-gray-900"
              }`}
            >
              <div className="flex flex-col h-full">
                <h3 className="text-2xl font-bold mb-4">{service.title}</h3>
                <p
                  className={`mb-6 flex-grow ${
                    service.colorScheme === "blue"
                      ? "text-blue-100"
                      : "text-gray-600"
                  }`}
                >
                  {service.description}
                </p>
                <Button
                  className={`w-full font-semibold group ${
                    service.colorScheme === "blue"
                      ? "bg-yellow-500 hover:bg-yellow-600 text-black"
                      : "bg-yellow-500 hover:bg-yellow-600 text-black"
                  }`}
                >
                  Learn More About{" "}
                  {service.title.split(" ").slice(0, 2).join(" ")}
                  <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Services;
