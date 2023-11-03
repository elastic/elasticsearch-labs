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

const sortSlice = createSlice({
    name: 'sort',
    initialState,
    reducers: {
        setSortOrder: (state, action: PayloadAction<{ key: string; sortDirection: sortDirection }>) => {
            const {key, sortDirection} = action.payload;
            state.sorts[key].sortDirection = sortDirection;
        },
    },
});

export const {setSortOrder} = sortSlice.actions;
export default sortSlice.reducer;
