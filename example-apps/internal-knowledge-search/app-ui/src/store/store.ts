import {configureStore} from '@reduxjs/toolkit';
import searchApplicationSettingsReducer from './slices/searchApplicationSettingsSlice';
import searchResultsReducer from './slices/searchResultsSlice';
import sortReducer from './slices/sortSlice';
import filterReducer from './slices/filterSlice';
import queryReducer from './slices/querySlice';

const store = configureStore({
    reducer: {
        searchApplicationSettings: searchApplicationSettingsReducer,
        searchResults: searchResultsReducer,
        sort: sortReducer,
        filter: filterReducer,
        query: queryReducer
    },
});

export type RootState = ReturnType<typeof store.getState>;
export default store;
