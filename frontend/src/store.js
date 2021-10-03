import {
    configureStore,
    getDefaultMiddleware
} from "@reduxjs/toolkit";

import {componentTagsStateSlice} from "./components/elements/element-detail-tabs/slice"
import {projectTagsStateSlice} from "./components/projects/project-view/slice";

const middleware = [
    ...getDefaultMiddleware(),
    /*YOUR CUSTOM MIDDLEWARES HERE*/
];

const store = configureStore({
    reducer: {
        componentTags: componentTagsStateSlice.reducer,
        projectTags: projectTagsStateSlice.reducer
    },
    middleware,
});

export default store;
window.store = store;