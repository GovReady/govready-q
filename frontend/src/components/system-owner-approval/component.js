import React, {useState} from 'react';
import ReactDOM from 'react-dom';
import {v4 as uuid_v4} from "uuid";
import { RequireApprovalModal } from './requireApprovalModal';
import { Provider } from "react-redux";
import store from "../../store";

window.requireApprovalModal = ( systemId, elementId, require_approval ) => {
    const uuid = uuid_v4();
    ReactDOM.render(
        <Provider store={store}>
            <RequireApprovalModal systemId={systemId} elementId={elementId} require_approval={require_approval} uuid={uuid} />
        </Provider>,
        document.getElementById('private-component-modal')
    );
};