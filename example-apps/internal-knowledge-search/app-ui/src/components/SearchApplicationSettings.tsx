import React, {useEffect, useState} from 'react';
import {useDispatch, useSelector} from "react-redux";
import {updateSettings} from "../store/slices/searchApplicationSettingsSlice";
import {useToast} from "../contexts/ToastContext";
import {MessageType} from "./Toast";
import {RootState} from "../store/store";



const SearchApplicationSettings: React.FC = () => {
    const dispatch = useDispatch();
    const {appName, appUser, appPassword, searchEndpoint, searchPersona, searchPersonaAPIKey} = useSelector((state: RootState) => state.searchApplicationSettings);
    const {showToast} = useToast();

    const fetchPersonaOptions = async () => {
        try {
            const searchAppIndices = await fetchSearchApplicationIndices()
            const identitiesIndex = await fetchIdentitiesIndex(searchAppIndices)
            const identitiesPath = searchEndpoint + "/" + identitiesIndex + "/_search"
            const response = await fetch(identitiesPath, {
                method: "POST",
                headers: {
                    "Authorization": "Basic " + btoa(appUser + ":" + appPassword),
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    "size": 30 //TODO: fix magic number. This is just how many identities I have in my data
                })
            });
            const jsonData = await response.json();
            const ids = jsonData.hits.hits.map((hit) => hit._id)
            return ids
        } catch (e) {
            console.log("Something went wrong tying to fetch ACL identities")
            console.log(e)
            return ["admin"]
        }
    }

    const fetchSearchApplicationIndices = async () => {
        try {
            const searchApplicationPath = searchEndpoint + "/_application/search_application/" + appName
            const response = await fetch(searchApplicationPath, {
                headers: {
                    "Authorization": "Basic " + btoa(appUser + ":" + appPassword)
                }
            })
            const jsonData = await response.json();
            const indices = jsonData.indices
            return indices
        } catch (e) {
            console.log("Something went wrong trying to fetch the Search Application underlying indices")
            console.log(e)
            return []
        }
    }

    const fetchIdentitiesIndex = async(applicationIndices) => {
        try {
            const identitiesIndexPath = searchEndpoint + "/.search-acl-filter*"
            const response = await fetch(identitiesIndexPath, {
                headers: {
                    "Authorization": "Basic " + btoa(appUser + ":" + appPassword)
                }
            })
            const jsonData = await response.json();
            const identityIndices = Object.keys(jsonData)
            const securedIndex = applicationIndices.find((applicationIndex) => identityIndices.includes(".search-acl-filter-"+applicationIndex))
            return ".search-acl-filter-"+securedIndex
        } catch (e) {
            console.log("Something went wrong trying to fetch the Identities Index")
            console.log(e)
            return
        }
    }

    const roleName = appName+"-key-role"
    const defaultRoleDescriptor = {
        [roleName]: {
            "cluster": [],
            "indices": [
                {
                    "names": [
                        appName
                    ],
                    "privileges": [
                        "read"
                    ],
                    "allow_restricted_indices": false
                }
            ],
            "applications": [],
            "run_as": [],
            "metadata": {},
            "transient_metadata": {
                "enabled": true
            },
            "restriction": {
                "workflows": [
                    "search_application_query"
                ]
            }
        }
    }
    const personaRoleDescriptor = async (persona) => {
        const identitiesIndex = ".search-acl-filter-search-sharepoint" //TODO fix hardcoded
        const identityPath = searchEndpoint + "/" + identitiesIndex + "/_doc/" + persona
        const response = await fetch(identityPath, {headers: {"Authorization": "Basic " + btoa(appUser + ":" + appPassword)}});
        const jsonData = await response.json();
        const permissions = jsonData._source.query.template.params.access_control
        return {
            "dls-role": {
                "cluster": ["all"],
                "indices": [
                    {
                        "names": [appName],
                        "privileges": ["read"],
                        "query" : {
                            "template": {
                                "params": {
                                    "access_control": permissions
                                },
                                "source" : `{
                                    "bool": {
                                        "filter": {
                                            "bool": {
                                                "should": [
                                                    {
                                                        "bool": {
                                                            "must_not": {
                                                                "exists": {
                                                                    "field": "_allow_access_control"
                                                                }
                                                            }
                                                        }
                                                    },
                                                    {
                                                        "terms": {
                                                            "_allow_access_control.enum": {{#toJson}}access_control{{/toJson}}
                                                        }
                                                    }
                                                ]
                                            }
                                        }
                                    }
                                }`
                            }
                        }
                    }
                ],
                "restriction": {
                    "workflows": [
                        "search_application_query"
                    ]
                }
            }
        }
    }
    const createPersonaAPIKey = async(persona) => {
        const roleDescriptor = persona == "admin" ? defaultRoleDescriptor : await personaRoleDescriptor(persona)
        const apiKeyPath = searchEndpoint + "/_security/api_key"
        const response = await fetch(apiKeyPath, {
            method: "POST",
            headers: {
                "Authorization": "Basic " + btoa(appUser + ":" + appPassword),
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                "name": appName+"-internal-knowledge-search-example-"+persona,
                "expiration": "1h",
                "role_descriptors": roleDescriptor,
                "metadata": {
                    "application": appName,
                    "createdBy": appUser
                }
            })
        })
        const jsonData = await response.json()
        return jsonData.encoded
    }

    const [searchPersonaOptions, setSearchPersonaOptions] = useState(["admin"]);

    // Populate personas dropdown options
    useEffect(() => {
        (async()=>{
            const fetchedPersonas = await fetchPersonaOptions()
            setSearchPersonaOptions(fetchedPersonas)
        })()
    },[])

    // Ensure we have an API key and override the "missing" default
    useEffect(() => {
        (async() => {
            if (searchPersonaAPIKey == "missing") {
                const createdAPIKey = await createPersonaAPIKey(searchPersona)
                updateSearchPersonaAPIKey(createdAPIKey)
            }
        })()
    }, [])

    // Ensure that the API key is updated when searchPersona changes
    useEffect( () => {
        (async() => {
            const apiKey = await createPersonaAPIKey(searchPersona);
            updateSearchPersonaAPIKey(apiKey);
        })()
    }, [searchPersona]);

    const [isOpen, setIsOpen] = useState(false);

    const toggleDropdown = () => {
        setIsOpen(!isOpen);
    };

    const handlePersonaChange = async (value: string) => {
        updateSearchPersona(value);
    };

    const handleSave = () => {
        dispatch(updateSettings({appName, appUser, appPassword, searchEndpoint, searchPersona, searchPersonaAPIKey}));
        showToast("Settings saved!", MessageType.Info);
    };

    const updateAppName = (e) => dispatch(updateSettings({appName: e.target.value, appUser, appPassword, searchEndpoint, searchPersona, searchPersonaAPIKey}))

    const updateAppUser = (e) => dispatch(updateSettings({appName, appUser: e.target.value, appPassword, searchEndpoint, searchPersona, searchPersonaAPIKey}))

    const updateAppPassword = (e) => dispatch(updateSettings({appName, appUser, appPassword: e.target.value, searchEndpoint, searchPersona, searchPersonaAPIKey}))

    const updateSearchEndpoint = (e) => dispatch(updateSettings({appName, appUser, appPassword, searchEndpoint: e.target.value, searchPersona, searchPersonaAPIKey}))

    const updateSearchPersona = (persona) => dispatch(updateSettings({appName, appUser, appPassword, searchEndpoint, searchPersona: persona, searchPersonaAPIKey}))

    const updateSearchPersonaAPIKey = (apiKey) => dispatch(updateSettings({appName, appUser, appPassword, searchEndpoint, searchPersona, searchPersonaAPIKey: apiKey}))

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
                    htmlFor="appUser"
                    className="block text-sm font-medium mb-1 text-gray-700"
                >
                    Search Application Username:
                </label>
                <p className="text-xs mb-2 text-gray-500">The Elasticsearch username to use to establish a connection with.</p>
                <input
                    id="appUser"
                    type="text"
                    value={appUser}
                    onChange={updateAppUser}
                    className="p-2 w-full border rounded focus:outline-none focus:shadow-outline"
                />
            </div>

            <div className="text-left mb-6 p-4 border rounded bg-gray-50">
                <label
                    htmlFor="appPassword"
                    className="block text-sm font-medium mb-1 text-gray-700"
                >
                    Application Elasticsearch Password:
                </label>
                <p className="text-xs mb-2 text-gray-500">The Elasticsearch password to use to establish a connection with.</p>
                <input
                    id="appPassword"
                    type="password"
                    value={appPassword}
                    onChange={updateAppPassword}
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

            <div className="text-left mb-6 p-4 border rounded bg-gray-50">
                <label
                    htmlFor="searchPersona"
                    className="block text-sm font-medium mb-1 text-gray-700"
                >
                    Search Persona:
                </label>
                <p className="text-xs mb-2 text-gray-500">The persona on whose behalf searches will be executed</p>
                <div className="relative">
                    <select
                        onChange={ async (event) => await handlePersonaChange(event.target.value)}
                        value={searchPersona}
                        className="flex items-center space-x-2 p-2 bg-white rounded border border-gray-300 focus:outline-none focus:border-blue-500"
                    >
                        {searchPersonaOptions.includes(searchPersona) ? "" : <option value={searchPersona} key={searchPersona} className="block text-left p-2 hover:bg-gray-100 cursor-pointer">
                            {searchPersona}
                        </option>}
                        {searchPersonaOptions.map((option, index) => (
                            <option value={option} key={option} className="block text-left p-2 hover:bg-gray-100 cursor-pointer">
                                {option}
                            </option>
                        ))}
                    </select>
                </div>
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
