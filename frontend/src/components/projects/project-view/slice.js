import {createSlice} from "@reduxjs/toolkit";

export const projectTagsStateSlice = createSlice({
    name: "projectTags",
    initialState: {
        value: []
    },
    reducers: {
        setTags: (state, action) => {
            state.value = action.payload;
        },
    },
});

