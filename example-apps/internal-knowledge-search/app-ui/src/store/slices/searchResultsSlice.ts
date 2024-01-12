import { createSlice } from '@reduxjs/toolkit';
import {SearchResultModel} from "../../models/SearchResultModel";

export interface SearchResultsState {
    results: SearchResultModel[];
}


const initialState: SearchResultsState = {
    results: []
};

export const searchResultsSlice = createSlice({
    name: 'searchResults',
    initialState,
    reducers: {
        updateSearchResults: (state, action) => {
            return action.payload;
        },
    },
});

export const { updateSearchResults } = searchResultsSlice.actions;
