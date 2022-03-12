import React, {useState} from 'react';
import ReactDOM from 'react-dom';
import { Permissions } from './permissions';

window.permissionsTable = () => {
  
    $(window).on('load', function () {
        $("#content").show();
        ReactDOM.render(
            <Permissions />,
            document.getElementById('perm-table')
        );
    });
};
