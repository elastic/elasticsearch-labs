import {configureStore} from '@reduxjs/toolkit';
import { searchApplicationSettingsSlice } from './slices/searchApplicationSettingsSlice';
import { searchResultsSlice } from './slices/searchResultsSlice';
import { sortSlice } from './slices/sortSlice';
import { filterSlice } from './slices/filterSlice';
import { querySlice } from './slices/querySlice';

export const store = configureStore({
    reducer: {
        searchApplicationSettings: searchApplicationSettingsSlice.reducer,
        searchResults: searchResultsSlice.reducer,
        sort: sortSlice.reducer,
        filter: filterSlice.reducer,
        query: querySlice.reducer
    },
});

export type RootState = ReturnType<typeof store.getState>;
