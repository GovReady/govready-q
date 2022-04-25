import React, { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { DataTable } from '../shared/table';
import axios from 'axios';
import moment from 'moment';
import { DataGrid } from '@mui/x-data-grid';
import { v4 as uuid_v4 } from "uuid";
import { 
  Grid,
} from '@mui/material';
import { makeStyles } from '@mui/styles';
import {
  Tooltip,
  Button,
  Glyphicon,
  OverlayTrigger,
  Col, 
  ControlLabel,
  Form,
  Checkbox,
  FormGroup, 
  Row,
  Modal
} from 'react-bootstrap';
import { AsyncPagination } from "../shared/asyncTypeahead";
import { red, green } from '@mui/material/colors';
import { ReactModal } from '../shared/modal';
import { hide, show } from '../shared/modalSlice';

const useStyles = makeStyles({
  root: {
    backgroundColor: 'orange',
    fontweight: 900,
  },
  table: {
    '& .datagrid-permission-header':{
      backgroundColor: 'blue',
    }
  },
  header: {
    '& .MuiDataGrid-columnHeaderTitleContainer':{
      flexFlow: 'row-reverse',
    },
  }
});

export const Permissions = ({ elementId, isOwner }) => {
  const dispatch = useDispatch();

  const classes = useStyles();
  const [usersList, setUsersList] = useState([]);
  const [permList, setPermList] = useState([]);
  const [permissibleUsers, setPermissibleUsers] = useState([]);
  const [open, setOpen] = useState(false);
  const [records, setRecords] = useState(0);
  const [sortby, setSortBy] = useState(["username", "asc"]);
  const [currentUser, setCurrentUser] = useState({});
  const editToolTip = (<Tooltip placement="top" id='tooltip-edit'> Edit User Permissions
  </Tooltip>)
  const showModal = useSelector(state => state.modal.value);

  const endpoint = (querystrings) => {
    return axios.get(`/api/v2/users/`, { params: querystrings });
  };

  useEffect(() => {
    axios(`/api/v2/users/`).then(response => {
        setUsersList(response.data.data);
    });
    axios(`/api/v2/element_permissions/${elementId}/`).then(response => {
        setPermList(response.data);
    });
  }, [])

  useEffect(() => {
    if(usersList.length > 0){
        setPermissibleUsers(getPermissibleUsers(permList));
    }
  }, [permList])

  const isObjectEmpty = (obj) => {
    return Object.keys(obj).length === 0;
  }

  const getPermissibleUsers = (data) => {
    let list = [];
    Object.entries(data.users_with_permissions).forEach(
      ([key, value]) => {
        const getUser = usersList.filter((user) => user.id === parseInt(key));
        const newUser = {
          id: uuid_v4(),
          user: getUser[0],
          view: value.includes('view_element'),
          change: value.includes('change_element'),
          add: value.includes('add_element'),
          delete: value.includes('delete_element'),
        }
        list.push(newUser);
      }
    );
    return list;      
  }
  const handleAddingNewUserPermissions = async (data) => {
    const permissible = { users_with_permissions: data }
    const response = await axios.put(`/api/v2/element_permissions/${elementId}/assign_role/`, permissible);
    if(response.status === 200){    
      // window.location.reload();
    } else {
      console.error("Something went wrong")
    }
  };

  const handleClickOpen = (row) => {
    setCurrentUser(row);
    dispatch(show());
  }
  
  const handleClose = () => {
    dispatch(hide());
  }
  
  const handleSubmit = async (event) => {
    const updatedUser = {
      id: currentUser.user.id,
      user: currentUser.user,
      view: currentUser.view,
      change: currentUser.change,
      add: currentUser.add,
      delete: currentUser.delete,
    }
    const permissible = { users_with_permissions: updatedUser }
    const response = await axios.put(`/api/v2/element_permissions/${elementId}/assign_role/`, permissible);
    if(response.status === 200){    
      // window.location.reload();
    } else {
      console.error("Something went wrong")
    }
  }

  const handleSave = (key, event) => {
    const updatedCurrentUser = {...currentUser};
    updatedCurrentUser[key] = !currentUser[key];
    setCurrentUser(updatedCurrentUser);
  }

  const handleRemoveUser = async (event) => {
    const remove_user = { user_to_remove: currentUser.user }
    const response = await axios.put(`/api/v2/element_permissions/${elementId}/remove_user/`, remove_user);
    if(response.status === 200){    
      window.location.reload();
      handleClose();
    } else {
      console.error("Something went wrong")
    }
  }

  const [columns, setColumns] = useState([
    {
      field: 'user',
      headerName: 'Username',
      width: 150,
      editable: false,
      valueGetter: (params) => params.row.user.username,
    },
    {
      field: 'email',
      headerName: 'Email',
      width: 300,
      editable: false,
      valueGetter: (params) => params.row.user.email,
    },
    {
      field: 'view',
      headerName: 'View',
      width: 100,
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
              {params.row.view ? <Glyphicon glyph="ok" style={{ color: green[700] }} /> : <Glyphicon glyph="remove" style={{ color: 'rgb(245,48,48,1)' }} />}
            </div>
          );
        },
    },
    {
      field: 'change',
      headerName: 'Change',
      width: 100,
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
              {params.row.change ? <Glyphicon glyph="ok" style={{ color: green[700] }} /> : <Glyphicon glyph="remove" style={{ color: 'rgb(245,48,48,1)' }} />}
            </div>
          );
        },
    },
    {
      field: 'add',
      headerName: 'Add',
      editable: false,
      width: 100,
      renderCell: (params) => {
        return (
          <div
            style={{ width: "100%" }}
            onClick={(e) => {
              e.stopPropagation();
              e.preventDefault();
            }}
          >
            {params.row.add ? <Glyphicon glyph="ok" style={{ color: green[700] }} /> : <Glyphicon glyph="remove" style={{ color: 'rgb(245,48,48,1)' }} />}
          </div>
        );
      },
    },
    {
      field: 'delete',
      headerName: 'Delete',
      width: 100,
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
              {params.row.delete ? <Glyphicon glyph="ok" style={{ color: green[700] }} /> : <Glyphicon glyph="remove" style={{ color: 'rgb(245,48,48,1)' }} />}
            </div>
          );
        },
    },
  ]);

  const [columnsForEditor, setColumnsForEditor] = useState([
    {
      field: 'user',
      headerName: 'Username',
      width: 150,
      editable: false,
      valueGetter: (params) => params.row.user.username,
    },
    {
      field: 'email',
      headerName: 'Email',
      width: 300,
      editable: false,
      valueGetter: (params) => params.row.user.email,
    },
    {
      field: 'view',
      headerName: 'View',
      width: 100,
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
              {params.row.view ? <Glyphicon glyph="ok" style={{ color: green[700] }} /> : <Glyphicon glyph="remove" style={{ color: 'rgb(245,48,48,1)' }} />}
            </div>
          );
        },
    },
    {
      field: 'change',
      headerName: 'Change',
      width: 100,
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
              {params.row.change ? <Glyphicon glyph="ok" style={{ color: green[700] }} /> : <Glyphicon glyph="remove" style={{ color: 'rgb(245,48,48,1)' }} />}
            </div>
          );
        },
    },
    {
      field: 'add',
      headerName: 'Add',
      editable: false,
      width: 100,
      renderCell: (params) => {
        return (
          <div
            style={{ width: "100%" }}
            onClick={(e) => {
              e.stopPropagation();
              e.preventDefault();
            }}
          >
            {params.row.add ? <Glyphicon glyph="ok" style={{ color: green[700] }} /> : <Glyphicon glyph="remove" style={{ color: 'rgb(245,48,48,1)' }} />}
          </div>
        );
      },
    },
    {
      field: 'delete',
      headerName: 'Delete',
      width: 100,
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
              {params.row.delete ? <Glyphicon glyph="ok" style={{ color: green[700] }} /> : <Glyphicon glyph="remove" style={{ color: 'rgb(245,48,48,1)' }} />}
            </div>
          );
        },
    },
    {
      field: 'edit',
      headerName: 'Edit Party',
      headerAlign: 'right',
      width: 150,
      editable: false,
      renderCell: (params) => {
        return (
          <div
            style={{ width: "100%", textAlign: 'end' }}
            onClick={(e) => {
              e.stopPropagation();
              e.preventDefault();
            }}
          >
            <div onClick={(e) => {
              e.stopPropagation();
              e.preventDefault();
              handleClickOpen(params.row)
            }}>
              <OverlayTrigger placement="right" overlay={editToolTip}>
                <Glyphicon glyph="pencil" style={{ color: '#3d3d3d' }} />
              </OverlayTrigger>
            </div>
          </div>
        );
      },
    },
  ]);
  
  return (
    <div style={{ maxHeight: '1000px', width: '100%' }}>
      <Grid
        container
        spacing={1}
        alignItems="flex-end"
        style={{ width: "100%" }}
      >
        <div style={{width: "calc(100% - 1rem - 25px)", marginTop: "1rem" }}>
          <div style={{ width: "100%", marginBottom: "1rem", display: "flex", justifyContent: "space-between" }}>
            <h2>Permissions</h2>
            </div>
        </div>
        {isOwner && 
          <Grid className="search-for-a-user-toolbar" item style={{ width: "calc(100% - 1rem - 25px)" }}>
            <br />
             <AsyncPagination
                endpoint={endpoint}
                order={"username"}
                primaryKey={'username'}
                secondarykey={'username'}
                onSelect={(selected) => {
                  if (selected.length > 0) {
                    const newUser = selected.map((user) => {
                        return {
                          id: uuid_v4(),
                          user: user,
                          view: true,
                          change: true,
                          add: false,
                          delete: false,
                        };
                    });
                    setPermissibleUsers((prev) => [...prev, newUser[0]]);
                    handleAddingNewUserPermissions(newUser[0]);
                  }
                }}
                excludeIds={permissibleUsers.map((du) => du.user.id)}
                defaultSelected 
                searchBarLength={"100%"}
                placeholder={"Search for a user..."}
            />
          </Grid>
        }
      </Grid>
      <br />
      <Grid className="permissible-users-data-grid" sx={{ minHeight: '200px' }}>
        <div style={{width: "calc(100% - 1rem - 25px)", marginTop: "1rem" }}>
          <DataGrid
            className={classes.table}
            autoHeight={true}
            density="compact"
            rows={permissibleUsers}
            columns={isOwner ? columnsForEditor : columns}
            pageSize={25}
            rowsPerPageOptions={[25]}
            checkboxSelection
            // onSelectionModelChange={(selectionModel, details) => {
            //   console.log(selectionModel, details);
            // }}
            // disableSelectionOnClick
            sx={{ 
              fontSize: '14px',
              '& .MuiDataGrid-columnHeaderTitle':{
                fontWeight: 600,
              },
            }}
          />
        </div>
      </Grid>
      {!isObjectEmpty(currentUser) && <ReactModal
          title={`User Permissions`}
          show={showModal}
          hide={() => dispatch(hide())}
          header={
            <Form horizontal>
              <>
                <FormGroup controlId={`form-title`}>
                  <Col sm={12}>
                    <h3>Edit {currentUser.user.username} permissions</h3>
                  </Col>
                </FormGroup>
              </>
            </Form>
          }
          body={
            <Form horizontal onSubmit={handleSubmit}>
              <FormGroup>
                <Row>
                  <Col componentClass={ControlLabel} sm={2}>
                      {'View'}
                  </Col>
                  <Col sm={10}>
                    <Checkbox 
                      checked={currentUser.view}
                      onChange={(event) => handleSave('view', event.target.value)}
                    />
                  </Col>
                  <Col componentClass={ControlLabel} sm={2}>
                      {'Add'}
                  </Col>
                  <Col sm={10}>
                    <Checkbox 
                      checked={currentUser.add}
                      onChange={(event) => handleSave('add', event.target.value)}
                    />
                  </Col>
                  <Col componentClass={ControlLabel} sm={2}>
                      {'Change'}
                  </Col>
                  <Col sm={10}>
                    <Checkbox 
                      checked={currentUser.change}
                      onChange={(event) => handleSave('change', event.target.value)}
                    />
                  </Col>
                  <Col componentClass={ControlLabel} sm={2}>
                      {'Delete'}
                  </Col>
                  <Col sm={10}>
                    <Checkbox 
                      checked={currentUser.delete}
                      onChange={(event) => handleSave('delete', event.target.value)}
                    />
                  </Col>
                </Row>
              </FormGroup>
              <Modal.Footer style={{width: 'calc(100% + 20px)'}}>
                  <Button type="button" bsStyle="danger" onClick={handleRemoveUser} style={{float: 'left'}}>Remove User</Button>
                  <Button variant="secondary" onClick={handleClose} style={{marginRight: '2rem'}}>Close</Button>
                  <Button type="submit" bsStyle="success">Save Changes</Button>
              </Modal.Footer>
              </Form>
          }
        />
      }
    </div>
  )
}