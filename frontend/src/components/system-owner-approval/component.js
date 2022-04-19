import React, {useState} from 'react';
import ReactDOM from 'react-dom';
import { RequireApprovalModal } from './requireApprovalModal';
import { Provider } from "react-redux";
import store from "../../store";

window.requireApprovalModal = ( systemId, is_owner ) => {
    $(window).on('load', function () {
        $("#content").show();
        ReactDOM.render(
            <Provider store={store}>
                <RequireApprovalModal systemId={systemId} isOwner={is_owner}/>
            </Provider>,
            document.getElementById('private-component-modal')
        );
    });
};