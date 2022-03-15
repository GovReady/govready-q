import React, {useState} from 'react';
import ReactDOM from 'react-dom';
import { Permissions } from './permissions';

window.permissionsTable = ( elementId ) => {
  
    $(window).on('load', function () {
        $("#content").show();
        ReactDOM.render(
            <Permissions elementId={elementId} />,
            document.getElementById('perm-table')
        );
    });
};
