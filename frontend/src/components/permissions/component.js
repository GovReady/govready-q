import React, {useState} from 'react';
import ReactDOM from 'react-dom';
import { PermissionsTable } from './permissionsTable';

window.permissionsTable = () => {
  
    $(window).on('load', function () {
        $("#content").show();
        ReactDOM.render(
            <PermissionsTable />,
            document.getElementById('perm-table')
        );
    });
};
