import {
    configureStore,
    getDefaultMiddleware
} from "@reduxjs/toolkit";

import {componentTagsStateSlice} from "./components/element-detail-tabs/slice"

const middleware = [
    ...getDefaultMiddleware(),
    /*YOUR CUSTOM MIDDLEWARES HERE*/
];

const store = configureStore({
    reducer: {
        componentTags: componentTagsStateSlice.reducer
    },
    middleware,
});

export default store;
window.store = store;