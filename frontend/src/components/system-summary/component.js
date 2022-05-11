import React, {useState} from 'react';
import ReactDOM from 'react-dom';
import { SystemSummary } from './system_summary';
import { SystemSummarySpreadsheet } from './system_summary_spreadsheet';
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

window.system_summary_spreadsheet = ( systemId, projectId ) => {
    ReactDOM.render(
        <Provider store={store}>
            <SystemSummarySpreadsheet systemId={systemId} projectId={projectId} />
        </Provider>,
        document.getElementById('system-summary-poam-spreadsheet-datagrid')
    );
};