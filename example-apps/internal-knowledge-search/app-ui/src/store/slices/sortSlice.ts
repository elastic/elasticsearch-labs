import {createSlice, PayloadAction} from '@reduxjs/toolkit';
import {SortModel, sortDirection} from "../../models/SortModel";

export interface SortState {
    sorts: {
        [key: string]: SortModel;
    };
}

const initialState: SortState = {
    sorts: {"createdAt": {"title": "Created at", sortDirection: "desc"}},
};

export const sortSlice = createSlice({
    name: 'sort',
    initialState,
    reducers: {
        setSortOrder: (state, action: PayloadAction<{ key: string; sortDirection: sortDirection }>) => {
            const {key, sortDirection} = action.payload;
            state.sorts[key].sortDirection = sortDirection;
            return state;
        },
    },
});

export const {setSortOrder} = sortSlice.actions;
