import {createSlice, PayloadAction} from '@reduxjs/toolkit';
import {FilterModel} from "../../models/FilterModel";

export interface FilterState {
    filters: { [label: string]: FilterModel };
}

const initialState: FilterState = {
    //TODO: fetch via API somewhere else
    filters: {
        "Data sources": {options: ["search-mongo", "search-mongo-2", "search-mysql", "search-sharepoint"], values: ["search-sharepoint"]}
    }
};

const filterSlice = createSlice({
    name: 'filter',
    initialState,
    reducers: {
        setFilterValue: (state, action: PayloadAction<{ label: string; values: string[] }>) => {
            state.filters[action.payload.label].values = action.payload.values;
        },
    },
});

export const {setFilterValue} = filterSlice.actions;
export default filterSlice.reducer;
