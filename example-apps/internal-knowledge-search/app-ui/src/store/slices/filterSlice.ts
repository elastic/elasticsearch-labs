import {createSlice, PayloadAction} from '@reduxjs/toolkit';
import {FilterModel} from "../../models/FilterModel";

export interface FilterState {
    filters: { [label: string]: FilterModel };
}

export const DATA_SOURCES = "Data Sources"

const initialState: FilterState = {
    filters: {
        [DATA_SOURCES]: {options: [], values: []}
    }
};


export const filterSlice = createSlice({
    name: 'filter',
    initialState,
    reducers: {
        addFilter: (state, action: PayloadAction<{ label: string}>) => {
            state.filters[action.payload.label] = { options: [], values: []}
        },
        resetFilters: (state) => {
            return initialState;
        },
        setFilterValue: (state, action: PayloadAction<{ label: string; values: string[] }>) => {
            state.filters[action.payload.label].values = action.payload.values;
            return state;
        },
        setFilterOptions:(state, action: PayloadAction<{ label: string; options: string[] }>) => {
            state.filters[action.payload.label].options = action.payload.options;
            // set all indices to true by default
            state.filters[action.payload.label].values = action.payload.options;
            return state;
        }
    },
});

export const {setFilterValue, setFilterOptions} = filterSlice.actions;
