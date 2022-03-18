import React, {useState} from 'react';
import ReactDOM from 'react-dom';
import { Permissions } from './permissions';
import { Provider } from "react-redux";
import store from "../../store";

window.permissionsTable = ( elementId ) => {
  
    $(window).on('load', function () {
        $("#content").show();
        ReactDOM.render(
            <Provider store={store}>
                <Permissions elementId={elementId} />
            </Provider>,
            document.getElementById('perm-table')
        );
    });
};
