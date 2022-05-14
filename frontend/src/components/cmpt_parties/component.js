import React, {useState} from 'react';
import ReactDOM from 'react-dom';
import { ComponentParties } from './cmpt_parties';
import { Provider } from "react-redux";
import store from "../../store";

window.cmptPartiesTable = ( elementId, poc_users, is_owner ) => {
    $(window).on('load', function () {
        $("#content").show();
        ReactDOM.render(
            <Provider store={store}>
                <ComponentParties elementId={elementId} poc_users={poc_users} isOwner={is_owner}/>
            </Provider>,
            document.getElementById('cmpt-parties-table')
        );
    });
};