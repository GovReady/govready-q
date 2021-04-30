import {createSlice} from "@reduxjs/toolkit";

export const componentTagsStateSlice = createSlice({
    name: "componentTags",
    initialState: {
        value: []
    },
    reducers: {
        setTags: (state, action) => {
            state.value = action.payload;
        },
    },
});

