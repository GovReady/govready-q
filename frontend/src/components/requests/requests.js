import React, { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { DataTable } from '../shared/table';
import axios from 'axios';
import moment from 'moment';
import { DataGrid, useGridApiContext } from '@mui/x-data-grid';
import { v4 as uuid_v4 } from "uuid";
import PropTypes from 'prop-types';
import { 
  Chip,
  Grid,
  Select,
  Stack,
} from '@mui/material';
import { makeStyles } from '@mui/styles';

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

  const handleSubmit = (params) => {
    console.log('handleSubmit');
    // {
    //   "user": 0,
    //   "system": 0,
    //   "requested_element": 0,
    //   "criteria_comment": "string",
    //   "criteria_reject_comment": "string",
    //   "status": "string"
    // }
    // const updatedRequest = {
    //   user: currentRequest.userId,
    //   system: currentRequest.system.id,
    //   requested_element: currentRequest.element.id,
    //   criteria_comment: currentRequest.criteria_comment,
    //   criteria_reject_comment: currentRequest.criteria_reject_comment,
    //   status: currentRequest.status,
    // }
    // const editRequestResponse = await axios.put(`/api/v2/elements/${elementId}/CreateAndSetRequest/`, updatedRequest);
    // if(editRequestResponse.status === 200){
    //   handleClose();
    // } else {
    //   console.error("Something went wrong in creating and setting new request to element");
    // }
  }

  const [columnsForEditor, setColumnsForEditor] = useState([
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
    // {
    //   field: 'action',
    //   headerName: 'Action',
    //   width: 300,
    //   editable: true,
    //   type: 'text',
    //   renderCell: (params) => (
    //     <Grid container rowSpacing={1} columnSpacing={{ xs: 1, sm: 2, md: 3 }}>
    //     <Grid item xs={6}>
    //       <Select
    //         value={params.row.status}
    //         onChange={() => handleChange(params, event.target.value)}
    //         size="small"
    //         sx={{ height: 1 }}
    //         native
    //         autoFocus
    //       >
    //         <option>Started</option>
    //         <option>Pending</option>
    //         <option>In Progress</option>
    //         <option>Complete</option>
    //       </Select>
    //     </Grid>
    //     <Grid item xs={6}>
    //       <Button variant="primary" onClick={handleSubmit(params)}>Submit</Button>
    //     </Grid>
    //   </Grid>
    //   ),
    // },
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
                        experimentalFeatures={{ newEditingApi: true}}
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