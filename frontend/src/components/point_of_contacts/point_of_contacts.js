import React, { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { DataTable } from '../shared/table';
import axios from 'axios';
import moment from 'moment';
import { DataGrid } from '@mui/x-data-grid';
import { v4 as uuid_v4 } from "uuid";
import { 
  Chip,
  Grid,
  Stack,
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
  const [openPartyModal, setOpenPartyModal] = useState(false);
  const [openRoleModal, setOpenRoleModal] = useState(false);
  const [records, setRecords] = useState(0);
  const [sortby, setSortBy] = useState(["name", "asc"]);
  const [currentParty, setCurrentParty] = useState({});
  const [removeAppointments, setRemovedAppointments] = useState([]);
  const editToolTip = (<Tooltip placement="top" id='tooltip-edit'> Edit POC</Tooltip>)

  const [example, setExample] = useState([]);
    const endpoint = (querystrings) => {
      return axios.get(`/api/v2/users/`, { params: querystrings });
    };

    useEffect(() => {
        axios(`/api/v2/elements/${elementId}/`).then(response => {
          console.log('response.data: ', response.data );
          setParties(response.data.parties);
        });
    }, [])

      const isObjectEmpty = (obj) => {
        return Object.keys(obj).length === 0;
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
    // dispatch(show());
    setOpenPartyModal(true);
  }
  const handleClickOpenRoles = (row) => {
    setCurrentParty(row);
    // dispatch(show());
    setOpenRoleModal(true);
  }
  const handleClose = () => {
    // dispatch(hide());
    setOpenPartyModal(false);
    setOpenRoleModal(false);
  }
  
  const handleSubmit = async (event) => {
    const updatedParty = {
      party_type: currentParty.party_type,
      name: currentParty.name,
      short_name: currentParty.short_name,
      email: currentParty.email,
      phone_number: currentParty.phone_number,
      mobile_phone: currentParty.mobile_phone
    }
    // const permissible = { users_with_permissions: updatedUser }
    const response = await axios.put(`/api/v2/parties/${currentParty.party_id}/`, updatedParty);
    if(response.status === 200){    
      // window.location.reload();
      console.log('UPDATED CORRECTLY!')
    } else {
      console.error("Something went wrong")
    }
  }

  const handleSave = (key, value) => {
    console.log('handleSave: ', key, value)
    const updatedCurrentParty = {...currentParty};
    updatedCurrentParty[key] = value;
    console.log('updatedCurrentParty: ', updatedCurrentParty);
    setCurrentParty(updatedCurrentParty);
  }

  const removeRoleFromCurrentParty = (index) => {
    const updatedCurrentParty = {...currentParty};
    const removedApt = updatedCurrentParty.roles.splice(index, 1);
    setRemovedAppointments([...removeAppointments, removedApt]);
    setCurrentParty(updatedCurrentParty);
  }

  
  const handleRoleSubmit = async (event) => {
    // event.preventDefault();
    const appointmentsList = [];
    removeAppointments.forEach(role => {
      appointmentsList.push(role[0].appointment_id);
    });

    const appointments = {
      "appointment_ids": appointmentsList
    };

    const response = await axios.put(`/api/v2/elements/${elementId}/removeAppointments/`, appointments);
    if(response.status === 200){    
      window.location.reload();
      handleClose();
    } else {
      console.error("Something went wrong")
    }
  }

  const handleRemoveParty = async (event) => {
    console.log('handleRemoveParty!')
    const remove_party = { 
      "party_id_to_remove": currentParty.party_id 
    }
    const response = await axios.put(`/api/v2/elements/${elementId}/removeAppointmentsByParty/`, remove_party);
    if(response.status === 200){    
      window.location.reload();
      handleClose();
    } else {
      console.error("Something went wrong")
    }
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
      field: 'edit_party',
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
    {
      field: 'roles',
      headerName: 'Roles',
      width: 200,
      editable: false,
      renderCell: (params) => (
        <div style={{ width: "100%" }}>
          {params.row.roles.map((role, index) => (
            <div key={index}>
              <span>{role.role_title}</span>
              <br/>
            </div>
          ))}
        </div>
      ),
    },
    {
      field: 'edit_roles',
      headerName: 'Edit Roles',
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
              handleClickOpenRoles(params.row)
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
  
  console.log('parties: ', parties)
  console.log('currentParty: ', currentParty)
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
          show={openPartyModal}
          hide={() => setOpenPartyModal(false)}
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
                        onChange={(event) => handleSave('name', event.target.value)}
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
                        onChange={(event) => handleSave('email', event.target.value)}
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
                        onChange={(event) => handleSave('phone_number', event.target.value)}
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
      {!isObjectEmpty(currentParty) && <ReactModal
          title={`Edit Party Roles`}
          show={openRoleModal}
          hide={() => setOpenRoleModal(false)}
          header={
            <Form horizontal>
              <>
                <FormGroup controlId={`form-title`}>
                  <Col sm={12}>
                    <h3>Edit {currentParty.name} roles</h3>
                  </Col>
                </FormGroup>
              </>
            </Form>
          }
          body={
            <Form horizontal onSubmit={handleRoleSubmit}>
              <FormGroup>
                {currentParty.roles.map((role, index) => (
                  <Row key={index}>
                    <Col componentClass={ControlLabel} sm={2}>
                      {role.role_title}
                    </Col>
                    <Col sm={10}>
                      {/* <FormControl
                        type="text"
                        placeholder={'Enter text'}
                        value={role.role_title}
                        onChange={(event) => handleSaveRole(index, 'role_title', event.target.value)}
                      /> */}
                      
                      {/** Delete button to remove role by index */}
                      <div onClick={(e) => {
                        e.stopPropagation();
                        e.preventDefault();
                        // handleClickOpenRoles(params.row)
                        removeRoleFromCurrentParty(index)
                      }}>
                        <OverlayTrigger placement="right" overlay={editToolTip}>
                          <Glyphicon glyph="pencil" style={{ color: '#3d3d3d' }} />
                        </OverlayTrigger>
                      </div>
                    </Col>
                  </Row>
                ))
                }
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