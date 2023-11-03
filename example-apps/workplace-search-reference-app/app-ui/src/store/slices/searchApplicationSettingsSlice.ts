import {createSlice, PayloadAction} from '@reduxjs/toolkit';
import {SearchApplicationSettingsModel} from "../../models/SearchApplicationSettingsModel";
const initialState: SearchApplicationSettingsModel = {
    appName: process.env.SEARCH_APP_NAME || "some-search-application",
    apiKey: process.env.SEARCH_APP_API_KEY || "xxxxxxxxxxxxxxxxxxx",
    searchEndpoint: process.env.SEARCH_APP_ENDPOINT || "https://some-search-end-point.co",
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
