import React, {useState} from 'react';
import ReactDOM from 'react-dom';
import { PointOfContacts } from './point_of_contacts';
import { Provider } from "react-redux";
import store from "../../store";

window.pocTable = ( elementId, is_owner ) => {
    $(window).on('load', function () {
        $("#content").show();
        ReactDOM.render(
            <Provider store={store}>
                <PointOfContacts elementId={elementId} isOwner={is_owner}/>
            </Provider>,
            document.getElementById('poc-table')
        );
    });
};