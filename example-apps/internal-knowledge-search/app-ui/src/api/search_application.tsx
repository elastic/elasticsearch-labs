import { useDispatch } from "react-redux";
import { callApi } from "./call_api";
import {
  updateSearchEndpoint,
  updateSearchPersonaAPIKey,
} from "store/slices/searchApplicationSettingsSlice";
import { DATA_SOURCES, setFilterOptions } from "store/slices/filterSlice";
import { AnyAction, Dispatch } from "redux";

export const fetchPersonas = async (appName: string) => {
  try {
    const response = await callApi<string[]>(
      "/api/persona?" + new URLSearchParams({ app_name: appName }),
      {
        method: "GET",
      }
    );
    return response;
  } catch (e) {
    console.log("Something went wrong tying to fetch ACL identities");
    console.log(e);
    return ["admin"];
  }
};

export const fetchApiKey = async (
  appName: string,
  persona: string,
  dispatch: Dispatch<AnyAction>
) => {
  try {
    const response = await callApi<{ api_key: string }>(
      "/api/api_key?" + new URLSearchParams({ app_name: appName, persona }),
      {
        method: "GET",
      }
    );
    dispatch(updateSearchPersonaAPIKey(response.api_key));
    return response.api_key;
  } catch (e) {
    console.log("Something went wrong tying to fetch API key");
    console.log(e);
    return "";
  }
};

export const fetchIndices = async (
  appName: string,
  dispatch: Dispatch<AnyAction>
) => {
  try {
    const response = await callApi<string[]>(
      "/api/indices?" + new URLSearchParams({ app_name: appName }),
      {
        method: "GET",
      }
    );
    dispatch(setFilterOptions({ label: DATA_SOURCES, options: response }));
    return response;
  } catch (e) {
    console.log(
      "Something went wrong tying to fetch search application indices"
    );
    console.log(e);
    return [];
  }
};

export const fetchDefaultSettings = async (dispatch: Dispatch<AnyAction>) => {
  try {
    const response = await callApi<{ elasticsearch_endpoint: string }>(
      "/api/default_settings",
      {
        method: "GET",
      }
    );
    dispatch(updateSearchEndpoint(response.elasticsearch_endpoint));
  } catch (e) {
    console.log(
      "Something went wrong tying to fetch search application indices"
    );
    console.log(e);
    return [];
  }
};
