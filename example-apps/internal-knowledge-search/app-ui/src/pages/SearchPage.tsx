import SearchBar from "../components/SearchBar";
import FilterBar from "../components/FilterBar";
import SearchResults from "../components/SearchResults";
import React, {useEffect, useState} from "react";

import SearchApplicationClient from '@elastic/search-application-client';
import {useDispatch, useSelector} from "react-redux";
import {useToast} from "../contexts/ToastContext";
import {updateSearchResults} from "../store/slices/searchResultsSlice";
import SortBar from "../components/SortBar";
import {MessageType} from "../components/Toast";
import dataSourceToLogoPathLookup from '../config/dataSourceToLogoPathLookup.json';
import documentsToSearchResultsMappings from '../config/documentsToSearchResultMappings.json';
import {RootState} from "../store/store";

const mapHitToSearchResult = (hit) => {
    const doc = hit._source;
    const dataSource = hit._index;
    const dataSourceImagePath = dataSource in dataSourceToLogoPathLookup ? dataSourceToLogoPathLookup[dataSource] : "";
    const dataSourceMapping = documentsToSearchResultsMappings[dataSource]

    return {
        title: doc[dataSourceMapping["title"]] || "No title",
        created: doc[dataSourceMapping["created"]] || "No creation date",
        previewText: doc[dataSourceMapping["previewText"]] || "No preview",
        fullText: doc[dataSourceMapping["fullText"]] || "No full text",
        dataSource: dataSource || "Data source unknown",
        dataSourceImagePath: dataSourceImagePath || "",
        link: doc[dataSourceMapping["link"]] || "Unknown"
    };
}

export default function SearchPage() {
    const dispatch = useDispatch();
    const {showToast} = useToast();
    const [loading, setLoading] = useState(false);
    //TODO: simplify query state and move it to one place
    const [query, setQuery] = useState<string>("");

    const {appName, apiKey: adminApiKey, searchEndpoint, searchPersona} = useSelector((state: RootState) => state.searchApplicationSettings);
    const {sorts} = useSelector((state: RootState) => state.sort);
    const indexFilter = useSelector((state: RootState) => state.filter)["filters"]["Data sources"].values;


    useEffect(() => {
        const fetchData = async () => await handleSearchSubmit();
        fetchData();
    }, [indexFilter, sorts, appName, adminApiKey, searchEndpoint]);

    const getOrCreateApiKey = async () => {
        if (searchPersona == "admin"){
            return adminApiKey
        }
        else {
            const identitiesIndex = ".search-acl-filter-search-sharepoint" //TODO fix hardcoded
            const identityPath = searchEndpoint + "/" + identitiesIndex + "/_doc/" + searchPersona
            const response = await fetch(identityPath, {headers: {"Authorization": "ApiKey " + adminApiKey}});
            const jsonData = await response.json();
            console.log(jsonData)
            const permissions = jsonData._source.query.template.params.access_control
            const apiKeyRoleDescriptor = {
                name: searchPersona,
                role_descriptors: {
                    "dls-role": {
                        "cluster": ["all"],
                        "indices": [
                            {
                                "names": ["search-sharepoint"],// TODO: hardcoded
                                "privileges": ["read"],
                                "query": {
                                    "template": {
                                        "params": {
                                            "permissions": permissions
                                        },
                                        'source': `
                                        {
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
                                                      "_allow_access_control": {{#toJson}}permissions{{/toJson}}
                                                    }
                                                  }
                                                ]
                                              }
                                            }
                                          }
                                        }
                                        `
                                    }
                                }
                            }
                        ]
                    }
                }
            }

            // TODO Use fetch: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API
            return "missing"
        }
    }

    const handleSearchSubmit = async () => {
        try {
            setLoading(true);

            const apiKey = await getOrCreateApiKey()
            showToast("API key is: "+apiKey)

            const client = SearchApplicationClient(appName, searchEndpoint, apiKey, {
                "facets": {
                    description: {
                        type: 'text',
                    },
                }
            })

            const sortArray = Object.values(sorts).map(sort => ({
                [sort.title]: sort.sortDirection,
            }));

            const rawResults = await client()
                .query(query)
                .setSort(sortArray)
                .setPageSize(10)
                .addParameter("indices", indexFilter)
                .search();

            const searchResults = rawResults.hits.hits
                .map((hit: any) => {
                    return mapHitToSearchResult(hit)
                });

            dispatch(updateSearchResults({results: searchResults}))
        } catch (e: unknown) {
            if (e instanceof Error) {
                showToast(e.message, MessageType.Error);
            } else {
                showToast('An unknown error occurred', MessageType.Error);
            }
        } finally {
            setLoading(false);
        }
    }

    const handleQueryChange = (query) => setQuery(query)

    return (
        <div className="min-h-screen">
            <SearchBar value={query} onSubmit={handleSearchSubmit} onQueryChange={handleQueryChange}/>
            <div className="flex items-center justify-center">
                <FilterBar/>
            </div>
            <div className="flex items-center justify-center">
                <SortBar/>
            </div>
            <div className="flex items-center justify-center mt-4">
                {loading ? (
                    <div className="text-blue-500 text-xl font-medium">Loading...</div>
                ) : (
                    <SearchResults/>
                )}
            </div>
        </div>
    )
}