import {createSlice, PayloadAction} from '@reduxjs/toolkit';

export interface QueryState {
    query: string;
}

const initialState: QueryState = {
    query: ""
};

export const querySlice = createSlice({
    name: 'query',
    initialState,
    reducers: {
        setQuery: (state, action: PayloadAction<string>) => {
            state.query = action.payload
            return state;
        },
    },
});

export const {setQuery} = querySlice.actions;
