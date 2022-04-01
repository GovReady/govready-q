import React, {useState} from 'react';
import ReactDOM from 'react-dom';
import { PointOfContacts } from './point_of_contacts';
import { Provider } from "react-redux";
import store from "../../store";

window.pocTable = ( elementId, poc_users, is_owner ) => {
    $(window).on('load', function () {
        $("#content").show();
        ReactDOM.render(
            <Provider store={store}>
                <PointOfContacts elementId={elementId} poc_users={poc_users} isOwner={is_owner}/>
            </Provider>,
            document.getElementById('poc-table')
        );
    });
};