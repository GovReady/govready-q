import {createSlice} from "@reduxjs/toolkit";

export const modalStateSlice = createSlice({
    name: "modal",
    initialState: {
        value: false
    },
    reducers: {
        hide: state => {
            state.value = false;
        },
        show: state => {
            state.value = true;
        }
    },
});

export const { hide, show } = modalStateSlice.actions;

export default modalStateSlice.reducer;