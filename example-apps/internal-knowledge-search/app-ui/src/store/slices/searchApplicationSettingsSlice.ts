import {createSlice, PayloadAction} from '@reduxjs/toolkit';
import {SearchApplicationSettingsModel} from "../../models/SearchApplicationSettingsModel";



const initialState: SearchApplicationSettingsModel = {
    appName: process.env.REACT_APP_SEARCH_APP_NAME || "some-search-application",
    appUser: process.env.REACT_APP_SEARCH_USER || "elastic",
    appPassword: process.env.REACT_APP_SEARCH_PASSWORD || "changeme",
    searchEndpoint: process.env.REACT_APP_SEARCH_APP_ENDPOINT || "https://some-search-end-point.co",
    searchPersona: "admin"
};

const searchApplicationSettingsSlice = createSlice({
    name: 'searchApplicationSettings',
    initialState,
    reducers: {
        updateSettings: (state, action: PayloadAction<SearchApplicationSettingsModel>) => {
            return action.payload;
        },
    },
});

export const { updateSettings } = searchApplicationSettingsSlice.actions;
export default searchApplicationSettingsSlice.reducer;
