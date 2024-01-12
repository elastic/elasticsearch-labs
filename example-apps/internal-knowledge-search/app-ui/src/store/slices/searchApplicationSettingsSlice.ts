import {createSlice, PayloadAction} from '@reduxjs/toolkit';
import {SearchApplicationSettingsModel} from "../../models/SearchApplicationSettingsModel";



const initialState: SearchApplicationSettingsModel = {
    appName: "some-search-application",
    indices: [],
    searchEndpoint: "https://some-search-end-point.co",
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

export const { updateAppName, updateIndices, updateSearchEndpoint, updateSearchPersona, updateSearchPersonaAPIKey } = searchApplicationSettingsSlice.actions;
