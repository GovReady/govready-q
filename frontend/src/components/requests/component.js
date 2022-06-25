import React, {useState} from 'react';
import ReactDOM from 'react-dom';
import { RequestsTable } from './requests';
import { Provider } from "react-redux";
import store from "../../store";

window.requestsTable = ( elementId, is_owner ) => {
    $(window).on('load', function () {
        $("#content").show();
        ReactDOM.render(
            <Provider store={store}>
                <RequestsTable elementId={elementId} isOwner={is_owner}/>
            </Provider>,
            document.getElementById('requests-table')
        );
    });
};