import React, { useEffect, useState } from 'react';
import { DataTable } from '../shared/table';
import axios from 'axios';
import moment from 'moment';
import { DataGrid } from '@mui/x-data-grid';
import { v4 as uuid_v4 } from "uuid";
import { Grid, } from '@mui/material';
import {
    Tooltip,
    Button,
    Glyphicon,
    OverlayTrigger,
} from 'react-bootstrap';
import { AsyncPagination } from "../shared/asyncTypeahead";

export const Permissions = () => {
    const [usersList, setUsersList] = useState([]);
    const [permList, setPermList] = useState([]);
    const [permissibleUsers, setPermissibleUsers] = useState([]);

    useEffect(() => {
        axios(`/api/v2/users/`).then(response => {
            setUsersList(response.data.data);
        });
        axios(`/api/v2/element_permissions/4/`).then(response => {
            setPermList(response.data);
        })
    }, [])

    useEffect(() => {
        if(usersList.length > 0){
            setPermissibleUsers(getPermissibleUsers(permList));
        }
    }, [permList])

    const editToolTip = (<Tooltip placement="top" id='tooltip-edit'> Edit User Permissions
    </Tooltip>)
    const [records, setRecords] = useState(0);
    const [sortby, setSortBy] = useState(["username", "asc"]);

    const [columns, setColumns] = useState([
        // { field: 'id', headerName: 'ID', width: 90 },
        {
            field: 'user',
            headerName: 'Username',
            width: 150,
            editable: false,
            valueGetter: (params) => params.row.user.at(0).username,
        },
        {
            field: 'email',
            headerName: 'Email',
            width: 150,
            editable: false,
            valueGetter: (params) => params.row.user.at(0).email,
        },
        {
          field: 'add',
          headerName: 'Add',
          width: 150,
          editable: false,
          renderCell: (params) => {
            return (
              <div
                style={{ width: "100%" }}
                onClick={(e) => {
                  e.stopPropagation();
                  e.preventDefault();
                }}
              >
                {params.row.add ? <Glyphicon glyph="ok" style={{ color: '#3d3d3d' }} /> : <Glyphicon glyph="remove" style={{ color: '#3d3d3d' }} />}
              </div>
            );
          },
        },
        {
            field: 'change',
            headerName: 'Change',
            width: 150,
            editable: false,
            renderCell: (params) => {
                return (
                  <div
                    style={{ width: "100%" }}
                    onClick={(e) => {
                      e.stopPropagation();
                      e.preventDefault();
                    }}
                  >
                    {params.row.change ? <Glyphicon glyph="ok" style={{ color: '#3d3d3d' }} /> : <Glyphicon glyph="remove" style={{ color: '#3d3d3d' }} />}
                  </div>
                );
              },
        },
        {
            field: 'delete',
            headerName: 'Delete',
            width: 150,
            editable: false,
            renderCell: (params) => {
                return (
                  <div
                    style={{ width: "100%" }}
                    onClick={(e) => {
                      e.stopPropagation();
                      e.preventDefault();
                    }}
                  >
                    {params.row.delete ? <Glyphicon glyph="ok" style={{ color: '#3d3d3d' }} /> : <Glyphicon glyph="remove" style={{ color: '#3d3d3d' }} />}
                  </div>
                );
              },
        },
        {
            field: 'view',
            headerName: 'View',
            width: 150,
            editable: false,
            renderCell: (params) => {
                return (
                  <div
                    style={{ width: "100%" }}
                    onClick={(e) => {
                      e.stopPropagation();
                      e.preventDefault();
                    }}
                  >
                    {params.row.view ? <Glyphicon glyph="ok" style={{ color: '#3d3d3d' }} /> : <Glyphicon glyph="remove" style={{ color: '#3d3d3d' }} />}
                  </div>
                );
              },
        },
    ]);

    const endpoint = (querystrings) => {
        return axios.get(`/api/v2/users/`, { params: querystrings });
    };


    const getPermissibleUsers = (data) => {
        let list = [];

        Object.entries(data.users_with_permissions).forEach(
            ([key, value]) => {
                console.log(key, value)
                const getUser = usersList.filter((user) => user.id === parseInt(key));
                console.log('getUser: ', getUser)
                const newUser = {
                    id: uuid_v4(),
                    user: getUser,
                    view: true,
                    change: false,
                    add: false,
                    delete: false,
                }
                list.push(newUser);
            }
        );
        return list;      
    }


    console.log('permissibleUsers: ', permissibleUsers)
    return (
        <div>
            <br />
            <AsyncPagination
                endpoint={endpoint}
                order={"username"}
                onSelect={(selected) => {
                    console.log('selected: ', selected)
                    if (selected.length > 0) {
                        
                        const newUser = selected.map((user) => {
                            return {
                                id: uuid_v4(),
                                user: user,
                                view: true,
                                change: false,
                                add: false,
                                delete: false,
                            };
                        });
                        // debugger;
                        setPermissibleUsers((prev) => [...prev, newUser]);
                    }
                }}
                excludeIds={permissibleUsers.map((du) => du.user.at(0).id)}
            />
            <br />
            <div style={{ height: 400, width: '100%' }}>
            <DataGrid
                rows={permissibleUsers}
                columns={columns}
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
