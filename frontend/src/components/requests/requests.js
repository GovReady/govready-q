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

export const RequestsTable = ({ elementId, isOwner }) => {
  const dispatch = useDispatch();

  const classes = useStyles();
  const dgClasses = datagridStyles();
  const [data, setData] = useState([]);
  const [sortby, setSortBy] = useState(["name", "asc"]);

  useEffect(() => {
    axios(`/api/v2/elements/${elementId}/retrieveRequests/`).then(response => {
      setData(response.data.requested);
    });
  }, [])

  const statuses = ["pending", "incomplete", "complete", "Approval to Proceed", "Enabled", "Implemented", "Rejected"]
  const [columnsForEditor, setColumnsForEditor] = useState([
    {
      field: 'user',
      headerName: 'User',
      width: 150,
      editable: false,
      valueGetter: (params) => console.log(params),
    },
    {
      field: 'system',
      headerName: 'Requested by',
      width: 150,
      editable: false,
      valueGetter: (params) => params.row.system.name,
    },
    {
      field: 'point_of_contact',
      headerName: 'Point of Contact',
      width: 300,
      editable: false,
      renderCell: (params) => (
        <div>
          {params.row.user_name} {(params.row.user_phone_number) ? `(${params.row.user_phone_number})` : ''}
        </div>
      ),
    },
    // {
    //   field: 'point_of_contact',
    //   headerName: 'Point of Contact',
    //   width: 300,
    //   editable: false,
    //   valueGetter: (params) => params.row.system.point_of_contact,
    // },
    // {
    //   field: 'req_poc',
    //   headerName: 'RequestedPoint of Contact',
    //   width: 300,
    
    //   editable: false,
    //   valueGetter: (params) => params.row.requested_element.point_of_contact[0],
    // },
    {
      field: 'status',
      headerName: 'Status',
      width: 150,
      editable: false,
      valueGetter: (params) => params.row.status,
    },
    {
      field: 'action',
      headerName: 'Action',
      width: 300,
      editable: false,
      renderCell: (params) => (
        <div>
          Action bar and submit button
        </div>
      ),
    },
  ]);

  const [columns, setColumns] = useState([
    {
        field: 'user',
        headerName: 'User',
        width: 150,
        editable: false,
        valueGetter: (params) => params.row.system.user.full_name,
    },
    {
      field: 'system',
      headerName: 'Requested by',
      width: 150,
      editable: false,
      valueGetter: (params) => params.row.system.root_element.full_name,
    },
    // {
    //   field: 'email',
    //   headerName: 'Point of Contact',
    //   width: 300,
    //   editable: false,
    //   valueGetter: (params) => params.row.email,
    // },
    {
        field: 'status',
        headerName: 'Status',
        width: 150,
        editable: false,
        valueGetter: (params) => params.row.status,
    },
  ]);

  return (
      <div style={{ maxHeight: '2000px', width: '100%' }}>
          <Grid className="poc-data-grid" sx={{ minHeight: '500px' }}>
              <div style={{width: "calc(100% - 1rem - 25px)", marginTop: "1rem" }}>
                  <div style={{ width: "100%", marginBottom: "1rem", display: "flex", justifyContent: "space-between" }}>
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
              </div>
          </Grid>
      </div>
  )
}