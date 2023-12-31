import React from 'react';
import {useDispatch, useSelector} from "react-redux";
import {updateSettings} from "../store/slices/searchApplicationSettingsSlice";
import {useToast} from "../contexts/ToastContext";
import {MessageType} from "./Toast";
import {RootState} from "../store/store";

const SearchApplicationSettings: React.FC = () => {
    const dispatch = useDispatch();
    const {appName, apiKey, searchEndpoint} = useSelector((state: RootState) => state.searchApplicationSettings);
    const {showToast} = useToast();

    const handleSave = () => {
        dispatch(updateSettings({appName, apiKey, searchEndpoint}));
        showToast("Settings saved!", MessageType.Info);
    };

    const updateAppName = (e) => dispatch(updateSettings({appName: e.target.value, apiKey, searchEndpoint}))
    const updateApiKey = (e) => dispatch(updateSettings({appName, apiKey: e.target.value, searchEndpoint}))
    const updateSearchEndpoint = (e) => dispatch(updateSettings({appName, apiKey, searchEndpoint: e.target.value}))

    return (
        <div className="container mx-auto p-4 bg-white rounded shadow-md">
            <div className="mb-6 flex justify-between items-center">
                <h1 className="text-2xl font-semibold">Search Application Settings</h1>
                <a
                    href="https://www.elastic.co/guide/en/enterprise-search/current/search-applications.html"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-blue-500 hover:underline">
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
                <p className="text-xs mb-2 text-gray-500">The name used to identify your search application.</p>
                <input
                    id="appName"
                    type="text"
                    value={appName}
                    onChange={updateAppName}
                    className="p-2 w-full border rounded focus:outline-none focus:shadow-outline"
                />
            </div>

            <div className="text-left mb-6 p-4 border rounded bg-gray-50">
                <label
                    htmlFor="apiKey"
                    className="block text-sm font-medium mb-1 text-gray-700"
                >
                    API Key:
                </label>
                <p className="text-xs mb-2 text-gray-500">Your unique API key used for authentication.</p>
                <input
                    id="apiKey"
                    type="password"
                    value={apiKey}
                    onChange={updateApiKey}
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
                <p className="text-xs mb-2 text-gray-500">The endpoint URL where search queries will be sent.</p>
                <input
                    id="searchEndpoint"
                    type="text"
                    value={searchEndpoint}
                    onChange={updateSearchEndpoint}
                    className="p-2 w-full border rounded focus:outline-none focus:shadow-outline"
                />
            </div>

            <button
                onClick={handleSave}
                className="mt-4 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
            >
                Save Settings
            </button>
        </div>

    );
}

export default SearchApplicationSettings;
