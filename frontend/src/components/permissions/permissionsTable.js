import React, { useState } from 'react';
import { DataTable } from '../shared/table';
import axios from 'axios';
import moment from 'moment';
import { DataGrid } from '@mui/x-data-grid';

import { Grid, } from '@mui/material';
import {
    Tooltip,
    Button,
    Glyphicon,
    OverlayTrigger,
} from 'react-bootstrap';
import { AsyncPagination } from "../shared/asyncTypeahead";

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
    const [sortProjby, setProjSortBy] = useState(["id", "asc"]);
    const [projcolumns, setProjColumns] = useState([
        {
            display: "Id",
            sortKey: "id",
            renderCell: (obj) => {
                return <span>{obj.id}</span>
            }
        },
        // {
        //     display: "Name",
        //     sortKey: "name",
        //     renderCell: (obj) => {
        //         return <span>{obj.name}</span>
        //     }
        // },
    ]);
    const permColumns = [
        { field: 'id', headerName: 'ID', width: 90 },
        {
          field: 'add_element',
          headerName: 'add_element',
          width: 150,
          editable: true,
        },
        {
            field: 'change_element',
            headerName: 'change_element',
            width: 150,
            editable: true,
        },
        {
            field: 'delete_element',
            headerName: 'delete_element',
            width: 150,
            editable: true,
        },
        {
            field: 'view_element',
            headerName: 'view_element',
            width: 150,
            editable: true,
        },
        // {
        //   field: 'lastName',
        //   headerName: 'Last name',
        //   width: 150,
        //   editable: true,
        // },
        // {
        //   field: 'age',
        //   headerName: 'Age',
        //   type: 'number',
        //   width: 110,
        //   editable: true,
        // },
        // {
        //   field: 'fullName',
        //   headerName: 'Full name',
        //   description: 'This column has a value getter and is not sortable.',
        //   sortable: false,
        //   width: 160,
        //   valueGetter: (params) =>
        //     `${params.row.firstName || ''} ${params.row.lastName || ''}`,
        // },
      ];

    const rows = [
        { id: 2, add_element: true, change_element:true, delete_element: true, view_element: true},
        { id: 3, add_element: false, change_element:false, delete_element: false, view_element: true},
    ]
    // const rows = [
    //     { id: 1, lastName: 'Snow', firstName: 'Jon', age: 35 },
    //     { id: 2, lastName: 'Lannister', firstName: 'Cersei', age: 42 },
    //     { id: 3, lastName: 'Lannister', firstName: 'Jaime', age: 45 },
    //     { id: 4, lastName: 'Stark', firstName: 'Arya', age: 16 },
    //     { id: 5, lastName: 'Targaryen', firstName: 'Daenerys', age: null },
    //     { id: 6, lastName: 'Melisandre', firstName: null, age: 150 },
    //     { id: 7, lastName: 'Clifford', firstName: 'Ferrara', age: 44 },
    //     { id: 8, lastName: 'Frances', firstName: 'Rossini', age: 36 },
    //     { id: 9, lastName: 'Roxie', firstName: 'Harvey', age: 65 },
    //   ];

    const endpoint = (querystrings) => {
        return axios.get(`/api/v2/users/`, { params: querystrings });
    };
    const elementsendpoint = (querystrings) => {
        return axios.get(`/api/v2/element_permissions/4/`, { params: querystrings });
    };
    return (
        <div>
            {/* <br />
            <AsyncPagination
                endpoint={endpoint}
                order={"display_name"}
                onSelect={(selected) => {
                    console.log('selected: ', selected)
                //   if (selected.length > 0) {
                //     const newUser = selected.map((user) => {
                //       return {
                //         id: uuid_v4(),
                //         user: user,
                //         role: {
                //           display: "Editor",
                //           value: "EDITOR",
                //         },
                //       };
                //     })[0];
                //     setDocumentUsers((prev) => [...prev, newUser]);
                //   }
                }}
                excludeIds={99}
            /> */}
            <br />
            <h1>PERMISSION</h1>
            {/* <DataTable
                sortby={sortby}
                columns={columns}
                endpoint={endpoint}
                header={<h1>Users</h1>}
                onResponse={(response)=>{
                    setRecords(response.pages.total_records);
                }}
            />
            <DataTable
                sortby={sortProjby}
                columns={projcolumns}
                endpoint={elementsendpoint}
                header={<h1>elementsendpoint</h1>}
                onResponse={(response)=>{
                    setRecords(response.pages.total_records);
                }}
            /> */}
            <div style={{ height: 400, width: '100%' }}>
            <DataGrid
                rows={rows}
                columns={permColumns}
                pageSize={5}
                rowsPerPageOptions={[5]}
                checkboxSelection
                disableSelectionOnClick
            />
            </div>
        </div>
    
    )
    // return (
    //     <div>
    //         <Grid item style={{ width: "calc(100% - 1rem - 25px" }}>
    //               <br />
    //               <AsyncPagination
    //                 endpoint={endpoint}
    //                 order={"display_name"}
    //                 onSelect={(selected) => {
    //                     console.log('selected: ', selected)
    //                 //   if (selected.length > 0) {
    //                 //     const newUser = selected.map((user) => {
    //                 //       return {
    //                 //         id: uuid_v4(),
    //                 //         user: user,
    //                 //         role: {
    //                 //           display: "Editor",
    //                 //           value: "EDITOR",
    //                 //         },
    //                 //       };
    //                 //     })[0];
    //                 //     setDocumentUsers((prev) => [...prev, newUser]);
    //                 //   }
    //                 }}
    //                 excludeIds={99}
    //               />
    //               {/* <TextField
    //                 variant="standard"
    //                 label="Add User"
    //                 fullWidth={true}
    //               // onChange={(e) => doSearch(e.target.value)}
    //               /> */}
    //         </Grid>
    //     </div>
    // )
}
