import React, { useState } from 'react';
import { DataTable } from '../shared/table';
import axios from 'axios';
import moment from 'moment';
import {
    Tooltip,
    Button,
    Glyphicon,
    OverlayTrigger,
} from 'react-bootstrap';

export const PermissionsTable = () => {
    const [records, setRecords] = useState(0);
    const [sortby, setSortBy] = useState(["username", "asc"]);
    const [columns, setColumns] = useState([
        {
            display: "Username",
            sortKey: "username",
            renderCell: (obj) => {
                return <span>{obj.username}</span>
            }
        },
        {
            display: "Email",
            sortKey: "email",
            renderCell: (obj) => {
                return <span>{obj.email}</span>
            }
        },
    ]);

    const endpoint = (querystrings) => {
        return axios.get(`/api/v2/users/`, { params: querystrings });
    };

    return <DataTable
        sortby={sortby}
        columns={columns}
        endpoint={endpoint}
        header={<h1>Users</h1>}
        onResponse={(response)=>{
            setRecords(response.pages.total_records);
        }}
    />
}
