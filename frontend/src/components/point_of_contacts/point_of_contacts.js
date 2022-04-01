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
  FormControl,
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

export const PointOfContacts = ({ elementId, poc_users, isOwner }) => {
  const dispatch = useDispatch();

  const classes = useStyles();
  const [usersList, setUsersList] = useState([]);
  const [permList, setPermList] = useState([]);
  const [parties, setParties] = useState([]);
  const [open, setOpen] = useState(false);
  const [records, setRecords] = useState(0);
  const [sortby, setSortBy] = useState(["name", "asc"]);
  const [currentParty, setCurrentParty] = useState({});
  const editToolTip = (<Tooltip placement="top" id='tooltip-edit'> Edit POC</Tooltip>)

    //   const endpoint = (querystrings) => {
    //     return axios.get(`/api/v2/users/`, { params: querystrings });
    //   };

    useEffect(() => {
        console.log('SETTING INITIAL PARTIES')
        setParties(getParties(poc_users));
        // axios(`/api/v2/users/`).then(response => {
        //     setUsersList(response.data.data);
        // });
        // axios(`/api/v2/element_permissions/${elementId}/`).then(response => {
        //     setPermList(response.data);
        // });
    }, [])

    //   useEffect(() => {
    //     if(usersList.length > 0){
    //         setParties(getParties(permList));
    //     }
    //   }, [permList])

      const isObjectEmpty = (obj) => {
        return Object.keys(obj).length === 0;
      }

    const getParties = (data) => {
        let list = [];
        /* Iterating through the poc_users object and creating a new object with all fields of party */
        data.map((party) => {
            const newParty = {
                id: party.fields.uuid,
                created: party.fields.created,
                email: party.fields.email,
                mobile_phone: party.fields.mobile_phone,
                name: party.fields.name,
                party_type: party.fields.party_type,
                phone_number: party.fields.phone_number,
                short_name: party.fields.short_name,
                updated: party.fields.updated,
                user: party.fields.user,
            }
            list.push(newParty);
        });
        return list;      
    }
//   const handleAddingNewUserPermissions = async (data) => {
//     const permissible = { users_with_permissions: data }
//     const response = await axios.put(`/api/v2/element_permissions/${elementId}/assign_role/`, permissible);
//     if(response.status === 200){    
//       // window.location.reload();
//     } else {
//       console.error("Something went wrong")
//     }
//   };

  const handleClickOpen = (row) => {
    setCurrentParty(row);
    dispatch(show());
  }
  
  const handleClose = () => {
    dispatch(hide());
  }
  
  const handleSubmit = async (event) => {
    // const updatedUser = {
    //   id: currentUser.user.id,
    //   user: currentUser.user,
    //   view: currentUser.view,
    //   change: currentUser.change,
    //   add: currentUser.add,
    //   delete: currentUser.delete,
    // }
    // const permissible = { users_with_permissions: updatedUser }
    // const response = await axios.put(`/api/v2/element_permissions/${elementId}/assign_role/`, permissible);
    // if(response.status === 200){    
    //   // window.location.reload();
    // } else {
    //   console.error("Something went wrong")
    // }
    console.log('HANDLE SUBMIT!')
  }

  const handleSave = (key, event) => {
    console.log('handleSave!')
    // const updatedCurrentUser = {...currentUser};
    // updatedCurrentUser[key] = !currentUser[key];
    // setCurrentUser(updatedCurrentUser);
  }

  const handleRemoveParty = async (event) => {
    console.log('handleRemoveParty!')
    // const remove_user = { user_to_remove: currentUser.user }
    // const response = await axios.put(`/api/v2/element_permissions/${elementId}/remove_user/`, remove_user);
    // if(response.status === 200){    
    //   window.location.reload();
    //   handleClose();
    // } else {
    //   console.error("Something went wrong")
    // }
  }

const [columns, setColumns] = useState([
    {
        field: 'name',
        headerName: 'Name',
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
        field: 'phone_number',
        headerName: 'Phone #',
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
  ]);

  const [columnsForEditor, setColumnsForEditor] = useState([
    {
      field: 'name',
      headerName: 'Name',
      width: 150,
      editable: false,
      valueGetter: (params) => params.row.name,
    },
    {
      field: 'email',
      headerName: 'Email',
      width: 300,
      editable: false,
      valueGetter: (params) => params.row.email,
    },
    {
        field: 'phone_number',
        headerName: 'Phone #',
        width: 300,
        editable: false,
        valueGetter: (params) => params.row.phone_number,
    },
    {
      field: 'edit',
      headerName: 'Edit',
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
  
  // console.log('parties: ', parties)
  return (
    <div style={{ maxHeight: '1000px', width: '100%' }}>
      <Grid className="poc-data-grid" sx={{ minHeight: '400px' }}>
        <div style={{width: "calc(100% - 1rem - 25px", marginTop: "1rem" }}>
            <h1>Parties</h1>
          <DataGrid
            className={classes.table}
            autoHeight={true}
            density="compact"
            rows={parties}
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
      {!isObjectEmpty(currentParty) && <ReactModal
          title={`User Permissions`}
          header={
            <Form horizontal>
              <>
                <FormGroup controlId={`form-title`}>
                  <Col sm={12}>
                    <h3>Edit {currentParty.name} permissions</h3>
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
                        {'Name'}
                    </Col>
                    <Col sm={10}>
                    <FormControl 
                        type="text"
                        placeholder={'Enter text'} 
                        value={currentParty.name} 
                        onChange={(event) => console.log(event.target.value)}
                    />
                    </Col>
                    <Col componentClass={ControlLabel} sm={2}>
                        {'Email'}
                    </Col>
                    <Col sm={10}>
                    <FormControl 
                        type="text"
                        placeholder={'Enter text'} 
                        value={currentParty.email} 
                        onChange={(event) => console.log(event.target.value)}
                    />
                    </Col>
                    <Col componentClass={ControlLabel} sm={2}>
                        {'Phone Number'}
                    </Col>
                    <Col sm={10}>
                    <FormControl 
                        type="text"
                        placeholder={'Enter text'} 
                        value={currentParty.phone_number} 
                        onChange={(event) => console.log(event.target.value)}
                    />
                    </Col>
                </Row>
              </FormGroup>
              <Modal.Footer style={{width: 'calc(100% + 20px)'}}>
                  <Button type="button" bsStyle="danger" onClick={handleRemoveParty} style={{float: 'left'}}>Remove Party</Button>
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