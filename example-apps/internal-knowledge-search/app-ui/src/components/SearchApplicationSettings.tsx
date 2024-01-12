import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  updateAppName,
  updateSearchEndpoint,
  updateSearchPersona,
} from "../store/slices/searchApplicationSettingsSlice";
import { useToast } from "../contexts/ToastContext";
import { MessageType } from "./Toast";
import { RootState } from "../store/store";
import {
  fetchApiKey,
  fetchDefaultSettings,
  fetchIndices,
  fetchPersonas,
} from "api/search_application";

export const SearchApplicationSettings: React.FC = () => {
  const dispatch = useDispatch();
  const { appName, searchEndpoint, searchPersona } = useSelector(
    (state: RootState) => state.searchApplicationSettings
  );

  const [searchPersonaOptions, setSearchPersonaOptions] = useState(["admin"]);

  // Populate personas dropdown options
  useEffect(() => {
    (async () => {
      const fetchedPersonas = await fetchPersonas(appName);
      setSearchPersonaOptions(fetchedPersonas);
    })();
  }, [appName]);

  // Ensure that the API key is updated when searchPersona changes
  useEffect(() => {
    fetchApiKey(appName, searchPersona, dispatch);
  }, [appName, searchPersona]);

  // Set index filter options
  useEffect(() => {
    fetchIndices(appName, dispatch);
  }, [appName]);

  useEffect(() => {
    fetchDefaultSettings(dispatch);
  }, []);

  return (
    <div className="container mx-auto p-4 bg-white rounded shadow-md">
      <div className="mb-6 flex justify-between items-center">
        <h1 className="text-2xl font-semibold">Search Application Settings</h1>
        <a
          href="https://www.elastic.co/guide/en/enterprise-search/current/search-applications.html"
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm text-blue-500 hover:underline"
        >
          Learn more
        </a>
      </div>

      <div className="text-left mb-6 p-4 border rounded bg-gray-50">
        <label
          htmlFor="appName"
          className="block text-sm font-medium mb-1 text-gray-700"
        >
          Search Application Name:
        </label>
        <p className="text-xs mb-2 text-gray-500">
          The name used to identify your search application.
        </p>
        <input
          id="appName"
          type="text"
          value={appName}
          onChange={(e) => dispatch(updateAppName(e.target.value))}
          className="p-2 w-full border rounded focus:outline-none focus:shadow-outline"
        />
      </div>

      <div className="text-left mb-6 p-4 border rounded bg-gray-50">
        <label
          htmlFor="searchEndpoint"
          className="block text-sm font-medium mb-1 text-gray-700"
        >
          Search Endpoint:
        </label>
        <p className="text-xs mb-2 text-gray-500">
          The endpoint URL where search queries will be sent. Use your
          elasticsearch host to call Elasticsearch directly (you may need to
          disable CORS). Use http://localhost:3001/api/search_proxy to proxy
          calls through the backend.
        </p>
        <input
          id="searchEndpoint"
          type="text"
          value={searchEndpoint}
          onChange={(e) => dispatch(updateSearchEndpoint(e.target.value))}
          className="p-2 w-full border rounded focus:outline-none focus:shadow-outline"
        />
      </div>

      <div className="text-left mb-6 p-4 border rounded bg-gray-50">
        <label
          htmlFor="searchPersona"
          className="block text-sm font-medium mb-1 text-gray-700"
        >
          Search Persona:
        </label>
        <p className="text-xs mb-2 text-gray-500">
          The persona on whose behalf searches will be executed
        </p>
        <div className="relative">
          <select
            onChange={(event) =>
              dispatch(updateSearchPersona(event.target.value))
            }
            value={searchPersona}
            className="flex items-center space-x-2 p-2 bg-white rounded border border-gray-300 focus:outline-none focus:border-blue-500"
          >
            {searchPersonaOptions.includes(searchPersona) ? (
              ""
            ) : (
              <option
                value={searchPersona}
                key={searchPersona}
                className="block text-left p-2 hover:bg-gray-100 cursor-pointer"
              >
                {searchPersona}
              </option>
            )}
            {searchPersonaOptions.map((option, index) => (
              <option
                value={option}
                key={option}
                className="block text-left p-2 hover:bg-gray-100 cursor-pointer"
              >
                {option}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
};
