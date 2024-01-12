import React from "react";
import { FaGear, FaMagnifyingGlass } from "react-icons/fa6";
import { Link } from "react-router-dom";

const navItems = [
  { label: "Search", icon: <FaMagnifyingGlass />, route: "/search" },
  { label: "Settings", icon: <FaGear />, route: "/" },
];

export const SidebarMenu: React.FC = () => {
  return (
    <div className="bg-white p-6 w-64 border-r border-gray-200">
      <nav>
        {navItems.map((item) => (
          <Link
            key={item.label}
            to={item.route}
            className="flex items-center mb-4 text-gray-700 hover:bg-gray-100 p-2 rounded transition-colors duration-200"
          >
            <span className="mr-2">{item.icon}</span>
            {item.label}
          </Link>
        ))}
      </nav>

      <hr className="mt-auto mb-4 border-t border-gray-300" />

      <div className="mt-auto mb-4 flex flex-col items-center text-sm">
        <img
          src="/elastic_logo.png"
          alt="Elastic"
          className="h-5 w-auto mb-2"
        />
        <span>Powered by</span>
        <div className="flex justify-center space-x-2">
          <a
            href="https://www.elastic.co/guide/en/enterprise-search/current/search-applications.html"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-500 hover:underline"
          >
            Search apps
          </a>
          <span>&</span>
          <a
            href="https://www.elastic.co/guide/en/enterprise-search/current/connectors.html"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-500 hover:underline"
          >
            Connectors
          </a>
        </div>
      </div>
    </div>
  );
};
