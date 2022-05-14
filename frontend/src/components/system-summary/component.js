import React, {useState} from 'react';
import ReactDOM from 'react-dom';
import { SystemSummary } from './system_summary';
import { Provider } from "react-redux";
import store from "../../store";

window.system_summary = ( systemId, projectId ) => {
    ReactDOM.render(
        <Provider store={store}>
            <SystemSummary systemId={systemId} projectId={projectId} />
        </Provider>,
        document.getElementById('system-summary-poam-datagrid')
    );
};