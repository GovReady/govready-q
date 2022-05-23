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

const datagridStyles = makeStyles({
  root: {
    "& .MuiDataGrid-renderingZone": {
      maxHeight: "none !important"
    },
    "& .MuiDataGrid-cell": {
      lineHeight: "unset !important",
      maxHeight: "none !important",
      whiteSpace: "normal"
    },
    "& .MuiDataGrid-row": {
      maxHeight: "none !important"
    },
    "& .MuiDataGrid-main":{
      height: "30rem !important",
    },
    "& .MuiDataGrid-virtualScroller":{
      height: "30rem !important",
    }
  }
});


const useStyles = makeStyles({
  root: {
    fontweight: 900,
  },
  header: {
    '& .MuiDataGrid-columnHeaderTitleContainer':{
      flexFlow: 'row-reverse',
    },
  }
});

export const ComponentParties = ({ elementId, poc_users, isOwner }) => {

  const classes = useStyles();
  const dgClasses = datagridStyles();
  const [data, setData] = useState([]);
  const [columns, setColumns] = useState([]);
  const [openPartyModal, setOpenPartyModal] = useState(false);
  const [openRoleModal, setOpenRoleModal] = useState(false);
  const [openAddNewPartyModal, setOpenAddNewPartyModal] = useState(false);
  const [sortby, setSortBy] = useState(["name", "asc"]);
  const [currentParty, setCurrentParty] = useState({});
  const [validated, setValidated] = useState({
    party_type: null,
    name: null,
    short_name: null,
    email: null,  
    phone_number: null,
    mobile_phone: null,
    role: null,
  });
  const [editValidated, setEditValidated] = useState({
    party_type: null,
    name: null,
    short_name: null,
    email: null,  
    phone_number: null,
    mobile_phone: null,
    role: null,
  });
  const [isValid, setIsValid] = useState(false);
  const [isEditValid, setIsEditValid] = useState(false);
  const [removeAppointments, setRemovedAppointments] = useState([]);
  const [createNewParty, setCreateNewParty] = useState({
    party_type: '',
    name: '',
    short_name: '',
    email: '',  
    phone_number: '',
    mobile_phone: '',
    roles: [],
  });
  const [createNewRole, setCreateNewRole] = useState({
    role_id: '',
    title: '',
    short_name: '',
    description: '',
  });
  const [tempRoleToAdd, setTempRoleToAdd] = useState([]);
  const [partyNamesList, setPartyNamesList] = useState([]);
  const editToolTip = (<Tooltip placement="top" id='tooltip-edit'> Edit role</Tooltip>)
  const deleteToolTip = (<Tooltip placement="top" id='tooltip-edit'> Delete role</Tooltip>)

  const endpoint = (querystrings) => {
    return axios.get(`/api/v2/roles/`, { params: querystrings });
  };

  const partyEndpoint = (querystrings) => {
    return axios.get(`/api/v2/parties/`, { params: querystrings });
  }

  useEffect(() => {
      axios(`/api/v2/elements/${elementId}/`).then(response => {
        setData(response.data.parties);
        let names = [];
        response.data.parties.map(party => {
          names.push(party.name);
        });
        setPartyNamesList(names);
      });
      

  }, []);

  useEffect(() => {
    // Check if every value in validated is success or null
    let valid = Object.values(validated).map(val => {
      if (val === 'warning' || val === 'error') {
        return false;
      } else {
        return true;
      }
      
    });
    
    let hasRoles = createNewParty.roles.length > 0;
    let allAreTrue = valid.every(val => val === true);
    setIsValid(allAreTrue && hasRoles);
  }, [validated, createNewParty]);

  useEffect(() => {
    // Check if every value in validated is success or null
    let valid = Object.values(editValidated).map(val => {
      if (val === 'warning' || val === 'error') {
        return false;
      } else {
        return true;
      }
      
    });
    
    let allAreTrue = valid.every(val => val === true);
    setIsEditValid(allAreTrue);
  }, [editValidated, currentParty]);

  useEffect(() => {
    setColumns([
      {
        field: 'name',
        headerName: 'Party Name',
        width: 150,
        editable: false,
        valueGetter: (params) => params.row.name,
      },
      {
        field: 'email',
        headerName: 'Email',
        width: 300,
        editable: false,
        valueGetter: (params) => {
          if(params.row.email === ''){
            return '-';
          } else {
            return params.row.email;
          }
        },
      },
      {
        field: 'phone_number',
        headerName: 'Phone Number',
        width: 300,
        editable: false,
        valueGetter: (params) => {
          if(params.row.phone_number === ''){
            return '-';
          } else {
            return params.row.phone_number;
          }
        },
      },
      {
        field: 'displayRoles',
        headerName: 'Roles',
        headerAlign: 'center',
        width: 300,
        editable: false,
        renderCell: (params) => (
          <Grid container rowSpacing={1} columnSpacing={1} sx={{width: "100%", marginTop: "0.25rem", marginBottom: "1rem"}}>
            {params.row.roles.map((role, index) => (
              <Grid item key={index}>
                <Chip
                  variant="outlined"
                  size="small"
                  label={role.role_title}
                />
                </Grid>
            ))}
          </Grid>
        ),
      },
    ]);
  }, [data])

  const isObjectEmpty = (obj) => {
    return Object.keys(obj).length === 0;
  }

  const handleNewPartyModal = () => {
    setOpenAddNewPartyModal(true);
  }
  const handleClickOpen = (row) => {
    setCurrentParty(row);
    setOpenPartyModal(true);
  }
  const handleClickOpenRoles = (row) => {
    setCurrentParty(row);
    setOpenRoleModal(true);
  }
  const handleClose = () => {
    setOpenPartyModal(false);
    setOpenRoleModal(false);
    setOpenAddNewPartyModal(false);
    setCreateNewParty({
      party_type: '',
      name: '',
      short_name: '',
      email: '',  
      phone_number: '',
      mobile_phone: '',
      roles: [],
    });
    setValidated({
      party_type: null,
      name: null,
      short_name: null,
      email: null,  
      phone_number: null,
      mobile_phone: null,
      role: null,
    })
    setCurrentParty({})
  }
  const clearPartyInfo = () => {
    setCreateNewParty({
      party_type: '',
      name: '',
      short_name: '',
      email: '',  
      phone_number: '',
      mobile_phone: '',
      roles: [],
    });
    setCurrentParty({})
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
    
    const response = await axios.put(`/api/v2/parties/${currentParty.party_id}/`, updatedParty);
    if(response.status === 200){
      window.location.reload();
    } else {
      console.error("Something went wrong")
    }
  }

  const handleSave = (key, value) => {
    const updatedCurrentParty = {...currentParty};
    if (key === 'phone_number' || key === 'mobile_phone'){
      const re = /^[0-9\b]+$/;
      if (re.test(value) || value === '') {
        updatedCurrentParty[key] = value;
        setCurrentParty(updatedCurrentParty);
      }
    } else {
      updatedCurrentParty[key] = value;
      setCurrentParty(updatedCurrentParty);
    }
  }

  const removeRoleFromCurrentParty = (index) => {
    const updatedCurrentParty = {...currentParty};
    const removedApt = updatedCurrentParty.roles.splice(index, 1);
    setRemovedAppointments([...removeAppointments, removedApt]);
    setCurrentParty(updatedCurrentParty);
  }

  const removeRoleFromCreateNewParty = (role, index) => {
    const updatedCreateNewParty = {...createNewParty};
    const removedApt = updatedCreateNewParty.roles.splice(index, 1);
    setCreateNewParty((prev) => ({
      ...prev,
      roles: updatedCreateNewParty.roles
    }));
  }
  const addRoleOntoCurrentParty = (selected) => {
    /**
     * 1. Add temporary role to currentParty instance
     * 2. onSubmit: check all roles, 
     *    if currentParty has new roles comparatively to oldParty instance, then add those new roles
     *    else if currentParty doesnt have old roles, then remove those old roles
     */
    
    const translatedRole = {
      "id": selected[0].id,
      "role_id": selected[0].role_id,
      "role_name": selected[0].short_name,
      "title": selected[0].title,
    }
    const updatedCurrentParty = {...currentParty};
    const addRoleId = updatedCurrentParty.roles.push(translatedRole);
    setTempRoleToAdd([...tempRoleToAdd, addRoleId]);
    setCurrentParty(updatedCurrentParty);
  }

  const handleRoleSubmit = async (event) => {
    event.preventDefault();

    const addedAppointmentsList = [];
    const removedAppointmentsList = [];
    
    const allCurrentPartyRoleIds = currentParty.roles.map(role => role.id);
    const rolesToAddAndAppoint = currentParty.roles.filter(role => role.appointment_id === undefined);

    removeAppointments.forEach(role => {
      if(!allCurrentPartyRoleIds.includes(role[0].appointment_id) && role[0].appointment_id !== undefined){
        removedAppointmentsList.push(role[0].appointment_id);
      }
    });
    rolesToAddAndAppoint.forEach(role => {
      addedAppointmentsList.push(role.id);
    });

    const appointmentsToBeAdded = {
      "role_ids": {
        "party_id": currentParty.party_id,
        "roles": addedAppointmentsList
      }
    }
    const appointmentsToBeRemoved = {
      "appointment_ids": removedAppointmentsList
    };

    const removeResponse = await axios.put(`/api/v2/elements/${elementId}/removeAppointments/`, appointmentsToBeRemoved);
    if(removeResponse.status === 200){    
      if(addedAppointmentsList.length > 0){
        const addResponse = await axios.post(`/api/v2/elements/${elementId}/CreateAndSet/`, appointmentsToBeAdded);
        if(addResponse.status === 200){
          window.location.reload();
          handleClose();
        } else {
          console.error("Something went wrong in creating and appointing new appointments")
        }
      } else {
        window.location.reload();
        handleClose();
      }
    } else {
      console.error("Something went wrong in removing appointment roles")
    }
  }

  const handleRemoveParty = async (event) => {
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

  const handleAddNewPartySubmit = async () => {
    /**
     * We want to create a new party, create an appointment with a designated role, and then add that appointment to the element
     * If we add more than 1 role, we create an appointment for each one
     */

    if(createNewParty.id === undefined){
      // Brand new party that we have to create       
      const newParty = {
        party_type: createNewParty.party_type,
        name: createNewParty.name,
        short_name: createNewParty.short_name,
        email: createNewParty.email,
        phone_number: createNewParty.phone_number,
        mobile_phone: createNewParty.mobile_phone
      }
      //created party 
      const createAndSetNewParty = await axios.post(`/api/v2/parties/`, newParty);
      if(createAndSetNewParty.status === 201){    
        // we created the party, now we want to create appointments and set them to the element
        
        const appointmentsToBeAdded = {
          "role_ids": {
            "party_id": createAndSetNewParty.data.id,
            "roles": createNewParty.roles.map(role => role.id)
          }
        }
        const addNewResponse = await axios.post(`/api/v2/elements/${elementId}/CreateAndSet/`, appointmentsToBeAdded);
        if(addNewResponse.status === 200){
          window.location.reload();
          // handleClose();
        } else {
          console.error("Something went wrong in creating and appointing new appointments")
        }
      } else {
        console.error("Something went wrong in removing appointment roles")
      }
    } else {
      //Already known party
      const appointmentsToBeAdded = {
        "role_ids": {
          "party_id": createNewParty.id,
          "roles": createNewParty.roles.map(role => role.id)
        }
      }
      const addNewResponse = await axios.post(`/api/v2/elements/${elementId}/CreateAndSet/`, appointmentsToBeAdded);
      if(addNewResponse.status === 200){
        window.location.reload();
        // handleClose();
      } else {
        console.error("Something went wrong in creating and appointing new appointments")
      }
    }
  }

  const handleNewPartySave = (key, value) => {
    const updatedNewParty = {...createNewParty};
    if (key === 'phone_number' || key === 'mobile_phone'){
      const re = /^[0-9\b]+$/;
      if (re.test(value) || value === '') {
        updatedNewParty[key] = value;
        setCreateNewParty(updatedNewParty);
      }
    } else {
      updatedNewParty[key] = value;
      setCreateNewParty(updatedNewParty);
    }
  }

  
  const [columnsForEditor, setColumnsForEditor] = useState([
    {
      field: 'name',
      headerName: 'Party Name',
      width: 150,
      editable: false,
      valueGetter: (params) => params.row.name,
    },
    {
      field: 'email',
      headerName: 'Email',
      width: 300,
      editable: false,
      // valueGetter: (params) => params.row.email,
      valueGetter: (params) => {
        if(params.row.email === ''){
          return '-';
        } else {
          return params.row.email;
        }
      },
    },
    {
        field: 'phone_number',
        headerName: 'Phone #',
        width: 150,
        editable: false,
        // valueGetter: (params) => params.row.phone_number,
        valueGetter: (params) => {
          if(params.row.phone_number === ''){
            return '-';
          } else {
            return params.row.phone_number;
          }
        },
    },
    {
      field: 'edit_party',
      headerName: 'Edit Party',
      headerAlign: 'center',
      width: 100,
      editable: false,
      renderCell: (params) => {
        return (
          <div
            style={{ width: "100%", textAlign: 'center' }}
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
      field: 'displayRoles',
      headerName: 'Roles',
      headerAlign: 'center',
      width: 300,
      editable: false,
      renderCell: (params) => (
        <Grid container rowSpacing={1} columnSpacing={1} sx={{width: "100%", marginTop: "0.25rem", marginBottom: "1rem"}}>
          {params.row.roles.map((role, index) => (
            <Grid item key={index}>
              <Chip
                variant="outlined"
                size="small"
                label={role.role_title}
              />
              </Grid>
          ))}
        </Grid>
      ),
    },
    {
      field: 'edit_roles',
      headerName: 'Edit Roles',
      headerAlign: 'center',
      width: 150,
      editable: false,
      renderCell: (params) => {
        return (
          <div
            style={{ width: "100%", textAlign: 'center' }}
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

  const getPartyTypeValidation = () => {
    if(createNewParty.party_type === ''){
      if(validated.party_type === 'warning'){
        return 'warning';
      } else {
        setValidated((prev) => ({...prev, party_type: 'warning'}));
        return 'warning';
      }
    } else {
      if(validated.party_type !== 'success'){
        setValidated((prev) => ({...prev, party_type: 'success'}));
        return 'success';
      } else {
        return 'success';
      }
    }
  }
  
  const getPartyNameValidation = () => {
    if(createNewParty.name === ''){
      if(validated.name === 'warning'){
        return 'warning';
      } else {
        setValidated((prev) => ({...prev, name: 'warning'}));
        return 'warning';
      }
    }

    if (partyNamesList.includes(createNewParty.name)){
      if(validated.name === 'error'){
        return 'error';
      } else {
        setValidated((prev) => ({...prev, name: 'error'}));
        return 'error';
      }
    } else {
      if(validated.name !== 'success'){
        setValidated((prev) => ({...prev, name: 'success'}));
        return 'success';
      } else {
        return 'success';
      }
    }
  }

  const getPartyShortNameValidation = () => {
    if(createNewParty.short_name === ''){
      if(validated.short_name === 'warning'){
        return 'warning';
      } else {
        setValidated((prev) => ({...prev, short_name: 'warning'}));
        return 'warning';
      }
    } else {
      if(validated.short_name !== 'success'){
        setValidated((prev) => ({...prev, short_name: 'success'}));
        return 'success';
      } else {
        return 'success';
      }
    }
  }
  const getPartyEmailValidation = () => {
    const emailRegex = RegExp('[a-z0-9]+@[a-z]+\.[a-z]{2,3}');
    if (createNewParty.email.length === 0) {
      if(validated.email === null){
        return null;
      } else {
        setValidated((prev) => ({...prev, email: null}));
        return null;
      }
    } else {
      if (emailRegex.test(createNewParty.email)) {
        if(validated.email !== 'success'){
          setValidated((prev) => ({...prev, email: 'success'}));
          return 'success';
        } else {
          return 'success';
        }
      } else {
        if(validated.email !== 'error'){
          setValidated((prev) => ({...prev, email: 'error'}));
          return 'error';
        } else {
          return 'error';
        }
      }
    }
    
  }

  const getPartyPhoneValidation = () => {
    if (createNewParty.phone_number.length === 0) {
      if(validated.phone_number === null){
        return null;
      } else {
        setValidated((prev) => ({...prev, phone_number: null}));
        return null;
      }
    } 
    else {
      if (createNewParty.phone_number.length > 0 && createNewParty.phone_number.length < 8) {
        if(validated.phone_number === 'warning'){
          return 'warning';
        } else {
          setValidated((prev) => ({...prev, phone_number: 'warning'}));
          return 'warning';
        }
      } else if (createNewParty.phone_number.length > 8 && createNewParty.phone_number.length < 16) {
        if(validated.phone_number !== 'success'){
          setValidated((prev) => ({...prev, phone_number: 'success'}));
          return 'success';
        } else {
          return 'success';
        }
      } else {
        if(validated.phone_number !== 'error'){
          setValidated((prev) => ({...prev, phone_number: 'error'}));
          return 'error';
        } else {
          return 'error';
        }
      }
    }
  }
  const getPartyMobilePhoneValidation = () => {
    if (createNewParty.mobile_phone.length === 0) {
      if(validated.mobile_phone === null){
        return null;
      } else {
        setValidated((prev) => ({...prev, mobile_phone: null}));
        return null;
      }
    } 
    else {
      if (createNewParty.mobile_phone.length > 0 && createNewParty.mobile_phone.length < 8) {
        if(validated.mobile_phone === 'warning'){
          return 'warning';
        } else {
          setValidated((prev) => ({...prev, mobile_phone: 'warning'}));
          return 'warning';
        }
      } else if (createNewParty.mobile_phone.length > 8 && createNewParty.mobile_phone.length < 16) {
        if(validated.mobile_phone !== 'success'){
          setValidated((prev) => ({...prev, mobile_phone: 'success'}));
          return 'success';
        } else {
          return 'success';
        }
      } else {
        if(validated.mobile_phone !== 'error'){
          setValidated((prev) => ({...prev, mobile_phone: 'error'}));
          return 'error';
        } else {
          return 'error';
        }
      }
    }
  }

  const getEditPartyNameValidation = () => {
    if(data.length > 0 && currentParty.name !== undefined) {

      const initialCurrentParty = data[currentParty.id-1];
      const updatedPartyList = partyNamesList.filter((party) => party !== initialCurrentParty.name)

      if(currentParty.name === ''){
        if(editValidated.name === 'warning'){
          return 'warning';
        } else {
          setEditValidated((prev) => ({...prev, name: 'warning'}));
          return 'warning';
        }
      }

      if(initialCurrentParty.name === currentParty.name){
        if(editValidated.name === 'success'){
          return 'success';
        } else {
          setEditValidated((prev) => ({...prev, name: 'success'}));
          return 'success';
        }
      } else if (updatedPartyList.includes(currentParty.name)){
        if(editValidated.name === 'error'){
          return 'error';
        } else {
          setEditValidated((prev) => ({...prev, name: 'error'}));
          return 'error';
        }
      } else {
        if(editValidated.name !== 'success'){
          setEditValidated((prev) => ({...prev, name: 'success'}));
          return 'success';
        } else {
          return 'success';
        }
      }
    }
  }

  const getEditPartyEmailValidation = () => {
    if(data.length > 0 && currentParty.email !== undefined) {
      const emailRegex = RegExp('[a-z0-9]+@[a-z]+\.[a-z]{2,3}');

      if(currentParty.email === ''){
        if(editValidated.email === null){
          return null;
        } else {
          setEditValidated((prev) => ({...prev, email: null}));
          return null;
        }
      } else {
        // return 'success';
        if (emailRegex.test(currentParty.email)) {
          // return 'success';
          if(editValidated.email === 'success'){
            return 'success';
          } else {
            setEditValidated((prev) => ({...prev, email: 'success'}));
            return 'success';
          }
        } else {
          if(editValidated.email === 'error'){
            return 'error';
          } else {
            setEditValidated((prev) => ({...prev, email: 'error'}));
            return 'error';
          }
        }
      } 
    }
  }

  const getEditPartyPhoneValidation = () => {
    if (currentParty.phone_number.length === 0) {
      if(editValidated.phone_number === null){
        return null;
      } else {
        setEditValidated((prev) => ({...prev, phone_number: null}));
        return null;
      }
    } 
    else {
      if (currentParty.phone_number.length > 0 && currentParty.phone_number.length < 8) {
        if(editValidated.phone_number === 'warning'){
          return 'warning';
        } else {
          setEditValidated((prev) => ({...prev, phone_number: 'warning'}));
          return 'warning';
        }
      } else if (currentParty.phone_number.length > 8 && currentParty.phone_number.length < 16) {
        if(editValidated.phone_number !== 'success'){
          setEditValidated((prev) => ({...prev, phone_number: 'success'}));
          return 'success';
        } else {
          return 'success';
        }
      } else {
        if(editValidated.phone_number !== 'error'){
          setEditValidated((prev) => ({...prev, phone_number: 'error'}));
          return 'error';
        } else {
          return 'error';
        }
      }
    }
  }

  return (
    <div style={{ maxHeight: '2000px', width: '100%' }}>
      <Grid className="poc-data-grid" sx={{ minHeight: '500px' }}>
        <div style={{width: "calc(100% - 1rem - 25px)", marginTop: "1rem" }}>
          <div style={{ width: "100%", marginBottom: "1rem", display: "flex", justifyContent: "space-between" }}>
            <h2>Parties</h2>
            <Button 
              style={{ width: "150px", height: "40px", marginTop: "0.5rem" }}
              onClick={(e) => {
                e.stopPropagation();
                e.preventDefault();
                handleNewPartyModal();
              }}
            >
              Appoint new party
            </Button>
            </div>
          <DataGrid
            className={dgClasses.root}
            autoHeight={true}
            density="compact"
            rows={data}
            columns={isOwner ? columnsForEditor : columns}
            pageSize={25}
            rowsPerPageOptions={[25]}
            rowHeight={50}
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
              <FormGroup validationState={getEditPartyNameValidation()}>
                <Row style={{ marginBottom: '1rem'}}>
                    <Col componentClass={ControlLabel} sm={2}>
                      {'Name'}
                    </Col>
                    <Col sm={10}>
                      <FormControl 
                          type="text"
                          placeholder={'Enter text'} 
                          value={currentParty.name} 
                          onChange={(event) => handleSave('name', event.target.value)}
                          style={{ width: '80%'}}
                      />
                      <FormControl.Feedback />
                    </Col>
                </Row>
              </FormGroup>
              <FormGroup validationState={getEditPartyEmailValidation()}>
                <Row style={{ marginBottom: '1rem'}}>
                  <Col componentClass={ControlLabel} sm={2}>
                    {'Email'}
                  </Col>
                  <Col sm={10}>
                    <FormControl 
                        type="email"
                        placeholder={'Enter text'} 
                        value={currentParty.email} 
                        onChange={(event) => handleSave('email', event.target.value)}
                        style={{ width: '80%'}}
                    />
                    <FormControl.Feedback />
                  </Col>
                </Row>
              </FormGroup>
              <FormGroup validationState={getEditPartyPhoneValidation()}>
                <Row style={{ marginBottom: '1rem'}}>
                  <Col componentClass={ControlLabel} sm={2}>
                    {'Phone Number'}
                  </Col>
                  <Col sm={10}>
                    <FormControl 
                        type="text"
                        placeholder={'Enter text'} 
                        value={currentParty.phone_number} 
                        onChange={(event) => handleSave('phone_number', event.target.value)}
                        style={{ width: '80%'}}
                    />
                    <FormControl.Feedback />
                  </Col>
                </Row>
              </FormGroup>
              <Modal.Footer style={{width: 'calc(100% + 20px)'}}>
                  <Button type="button" bsStyle="danger" onClick={handleRemoveParty} style={{float: 'left'}}>Remove Party</Button>
                  <Button variant="secondary" onClick={handleClose} style={{marginRight: '2rem'}}>Close</Button>
                  <Button type="submit" bsStyle="success" disabled={!isEditValid}>Save Changes</Button>
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
                <div 
                  style={{ 
                    marginLeft: '6rem', 
                    marginBottom: '2rem', 
                    width: '80%', 
                  }}
                >
                  <AsyncPagination
                    endpoint={endpoint}
                    order={"title"}
                    primaryKey={'title'}
                    secondarykey={'title'}
                    onSelect={(selected) => {
                      if (selected.length > 0) {
                        /* 
                          Step 1: Create new appointment with chosen role
                          Step 2: Add appointment to parties instance
                          Step 3: Post new appointment to backend
                          Step 4: attach appointment to element component
                        */
                        addRoleOntoCurrentParty(selected);
                      }
                    }}
                    excludeIds={currentParty.roles.map((du) => du.id)}
                    defaultSelected 
                    searchBarLength={"100%"}
                    placeholder={"Search for a role..."}
                  />
                </div>
                {currentParty.roles.map((role, index) => (
                  <Row key={index}>
                    <Col componentClass={ControlLabel} sm={4} style={{ paddingLeft: '5rem', textAlign: 'left' }}>
                      {role.role_title}
                    </Col>
                    <Col sm={8}>
                      {/** Delete button to remove role by index */}
                      <div 
                        onClick={(e) => {
                          removeRoleFromCurrentParty(index)
                        }}
                        style={{
                          height: '20px',
                          width: '20px',
                        }}
                      >
                        <OverlayTrigger placement="right" overlay={deleteToolTip}>
                          <Glyphicon glyph="trash" style={{ color: '#3d3d3d' }} />
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
      {/** CREATE A NEW PARTY MODAL **/}
      <ReactModal
          title={`Create New Party with appointed roles`}
          show={openAddNewPartyModal}
          hide={() => setOpenAddNewPartyModal(false)}
          header={
            <Form horizontal>
              <>
                <FormGroup controlId={`form-title`}>
                  <Col sm={12}>
                    <h3>Add a new party</h3>
                  </Col>
                </FormGroup>
              </>
            </Form>
          }
          body={
            <Form horizontal onSubmit={handleAddNewPartySubmit}>
                <div 
                  style={{ 
                    marginLeft: '6rem', 
                    marginBottom: '2rem', 
                    width: '80%', 
                  }}
                >
                  <Row>
                    <AsyncPagination
                      endpoint={partyEndpoint}
                      order={"name"}
                      primaryKey={'name'}
                      secondarykey={'name'}
                      onSelect={(selected) => {
                        if (selected.length > 0) {
                          setCreateNewParty((prev) => ({
                            ...prev,
                            id: selected[0].id,
                            created: selected[0].created,
                            updated: selected[0].updated,
                            party_type: selected[0].party_type,
                            name: selected[0].name,
                            short_name: selected[0].short_name,
                            email: selected[0].email,  
                            phone_number: selected[0].phone_number,
                            mobile_phone: selected[0].mobile_phone,
                          }));
                        }
                      }}
                      excludeIds={data.map((du) => du.party_id)}
                      defaultSelected 
                      searchBarLength={"100%"}
                      placeholder={"Search for a party..."}
                    />
                  </Row>
                  <FormGroup validationState={getPartyTypeValidation()}>
                    <Row>
                      <Col componentClass={ControlLabel} sm={4} style={{ paddingLeft: '5rem', textAlign: 'left' }}>
                        {'Party Type'}
                      </Col>
                      <Col sm={8}>
                        <div>
                          <FormControl 
                            type="text"
                            placeholder={'Enter text'} 
                            value={createNewParty['party_type']}
                            readOnly={createNewParty.id !== undefined ? true : false}
                            onChange={(event) => handleNewPartySave('party_type', event.target.value)}
                            style={{ 
                              width: '80%',
                              marginTop: '0.5rem',
                              marginBottom: '0.5rem',
                            }}
                          />
                          <FormControl.Feedback />
                        </div>
                      </Col>
                    </Row>
                  </FormGroup>
                  <FormGroup validationState={createNewParty.id !== undefined ? getPartyNameValidation() : getEditPartyNameValidation()}>
                    <Row>
                      <Col componentClass={ControlLabel} sm={4} style={{ paddingLeft: '5rem', textAlign: 'left' }}>
                        {'Name'}
                      </Col>
                      <Col sm={8}>
                        <div>
                          <FormControl 
                            type="text"
                            placeholder={'Enter text'} 
                            value={createNewParty['name']}
                            readOnly={createNewParty.id !== undefined ? true : false}
                            onChange={(event) => handleNewPartySave('name', event.target.value)}
                            style={{ 
                              width: '80%',
                              marginTop: '0.5rem',
                              marginBottom: '0.5rem',
                            }}
                          />
                          <FormControl.Feedback />
                        </div>
                      </Col>
                    </Row>
                  </FormGroup>
                  <FormGroup validationState={getPartyShortNameValidation()}>
                    <Row>
                      <Col componentClass={ControlLabel} sm={4} style={{ paddingLeft: '5rem', textAlign: 'left' }}>
                        {'Short Name'}
                      </Col>
                      <Col sm={8}>
                        <div>
                          <FormControl 
                            type="text"
                            placeholder={'Enter text'} 
                            value={createNewParty['short_name']}
                            readOnly={createNewParty.id !== undefined ? true : false}
                            onChange={(event) => handleNewPartySave('short_name', event.target.value)}
                            style={{ 
                              width: '80%',
                              marginTop: '0.5rem',
                              marginBottom: '0.5rem',
                            }}
                          />
                          <FormControl.Feedback />
                        </div>
                      </Col>
                    </Row>
                  </FormGroup>
                  <FormGroup validationState={getPartyEmailValidation()}>
                    <Row>
                      <Col componentClass={ControlLabel} sm={4} style={{ paddingLeft: '5rem', textAlign: 'left' }}>
                        {'Email'}
                      </Col>
                      <Col sm={8}>
                        <div>
                          <FormControl 
                            type="email"
                            placeholder={'Enter text'} 
                            value={createNewParty['email']}
                            readOnly={createNewParty.id !== undefined ? true : false}
                            onChange={(event) => handleNewPartySave('email', event.target.value)}
                            style={{ 
                              width: '80%',
                              marginTop: '0.5rem',
                              marginBottom: '0.5rem',
                            }}
                          />
                          <FormControl.Feedback />
                        </div>
                      </Col>
                    </Row>
                  </FormGroup>
                  <FormGroup validationState={getPartyPhoneValidation()}>
                    <Row>
                      <Col componentClass={ControlLabel} sm={4} style={{ paddingLeft: '5rem', textAlign: 'left' }}>
                        {'Phone Number'}
                      </Col>
                      <Col sm={8}>
                        <div>
                          <FormControl 
                            type="text"
                            placeholder={'Enter text'} 
                            value={createNewParty['phone_number']}
                            readOnly={createNewParty.id !== undefined ? true : false}
                            onChange={(event) => handleNewPartySave('phone_number', event.target.value)}
                            style={{ 
                              width: '80%',
                              marginTop: '0.5rem',
                              marginBottom: '0.5rem',
                            }}
                          />
                          <FormControl.Feedback />
                        </div>
                      </Col>
                    </Row>
                  </FormGroup>
                  <FormGroup validationState={getPartyMobilePhoneValidation()}>
                    <Row>
                      <Col componentClass={ControlLabel} sm={4} style={{ paddingLeft: '5rem', textAlign: 'left' }}>
                        {'Mobile Phone Number'}
                      </Col>
                      <Col sm={8}>
                        <div>
                          <FormControl 
                            type="text"
                            placeholder={'Enter text'} 
                            value={createNewParty['mobile_phone']}
                            readOnly={createNewParty.id !== undefined ? true : false}
                            onChange={(event) => handleNewPartySave('mobile_phone', event.target.value)}
                            style={{ 
                              width: '80%',
                              marginTop: '0.5rem',
                              marginBottom: '0.5rem',
                            }}
                          />
                          <FormControl.Feedback />
                        </div>
                      </Col>
                    </Row>
                  </FormGroup>
                  <div 
                    style={{ 
                      // marginLeft: '6rem', 
                      marginBottom: '2rem', 
                      width: '80%', 
                    }}
                  >
                    <AsyncPagination
                      endpoint={endpoint}
                      order={"title"}
                      primaryKey={'title'}
                      secondarykey={'title'}
                      onSelect={(selected) => {
                        if (selected.length > 0) {
                          /* 
                            Step 1: Create new appointment with chosen role
                            Step 2: Add appointment to parties instance
                            Step 3: Post new appointment to backend
                            Step 4: attach appointment to element component
                          */
                          const updatedCreateNewParty = {...createNewParty};
                          const updatedRoles = updatedCreateNewParty.roles.push(selected[0]);
                          setCreateNewParty((prev) => ({
                            ...prev,
                            roles: updatedCreateNewParty.roles,
                          }));
                        }
                      }}
                      excludeIds={createNewParty.roles.map((du) => du.id)}
                      defaultSelected 
                      searchBarLength={"100%"}
                      placeholder={"Search for a role..."}
                    />
                </div>
                {createNewParty.roles.length > 0 ? createNewParty.roles.map((role, index) => (
                  <Row key={index}>
                    <Col componentClass={ControlLabel} sm={4} style={{ paddingLeft: '5rem', textAlign: 'left' }}>
                      {role.title}
                    </Col>
                    <Col sm={8}>
                      <div 
                        onClick={(e) => {
                          removeRoleFromCreateNewParty(role, index);
                        }}
                        style={{
                          height: '20px',
                          width: '20px',
                        }}
                      >
                        <OverlayTrigger placement="right" overlay={deleteToolTip}>
                          <Glyphicon glyph="trash" style={{ color: '#3d3d3d' }} />
                        </OverlayTrigger>
                      </div>
                    </Col>
                  </Row>
                )) : null
                }
                </div>
              <Modal.Footer style={{width: 'calc(100% + 20px)'}}>
                  <Button type="button" onClick={clearPartyInfo} style={{float: 'left'}}>Clear</Button>
                  <Button variant="secondary" onClick={handleClose} style={{marginRight: '2rem'}}>Close</Button>
                  <Button type="submit" bsStyle="success" disabled={!isValid}>Save Changes</Button>
              </Modal.Footer>
              </Form>
          }
        />

    </div>
  )
}