import {createSlice, PayloadAction} from '@reduxjs/toolkit';
import {SearchApplicationSettingsModel} from "../../models/SearchApplicationSettingsModel";



const initialState: SearchApplicationSettingsModel = {
    appName: process.env.REACT_APP_SEARCH_APP_NAME || "some-search-application",
    indices: [],
    searchEndpoint: process.env.REACT_APP_SEARCH_APP_ENDPOINT || "https://some-search-end-point.co",
    searchPersona: "admin",
    searchPersonaAPIKey: "missing"
};

export const searchApplicationSettingsSlice = createSlice({
    name: 'searchApplicationSettings',
    initialState,
    reducers: {
        updateAppName: (state, action: PayloadAction<string>) => {
            state.appName = action.payload;
            return state;
        },
        updateIndices: (state, action: PayloadAction<string[]>) => {
            state.indices = action.payload;
            return state;
        },
        updateSettings: (state, action: PayloadAction<SearchApplicationSettingsModel>) => {
            return action.payload;
        },
        updateSearchEndpoint: (state, action: PayloadAction<string>) => {
            state.searchEndpoint = action.payload;
            return state;
        },
        updateSearchPersona: (state, action: PayloadAction<string>) => {
            state.searchPersona = action.payload;
            return state;
        },
        updateSearchPersonaAPIKey: (state, action: PayloadAction<string>) => {
            state.searchPersonaAPIKey = action.payload;
            return state;
        }
    },
});

export const { updateAppName, updateIndices, updateSettings, updateSearchEndpoint, updateSearchPersona, updateSearchPersonaAPIKey } = searchApplicationSettingsSlice.actions;
