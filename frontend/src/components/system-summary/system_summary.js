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

export const SystemSummary = ({ systemId, projectId }) => {
  const dispatch = useDispatch();

  const classes = useStyles();
  const dgClasses = datagridStyles();
  const [data, setData] = useState([]);
  const [sortby, setSortBy] = useState(["name", "asc"]);

  useEffect(() => {
    axios(`/api/v2/systems/${systemId}/poams/`).then(response => {
      setData(response.data.data);
    });
  }, [])

  const [columns, setColumns] = useState([
    {
        field: 'weakness_name',
        headerName: 'POA&M',
        width: 150,
        editable: false,
        valueGetter: (params) => params.row.weakness_name,
      },
      {
        field: 'evidence',
        headerName: 'Evidence',
        width: 150,
        editable: false,
        valueGetter: (params) => params.row.weakness_name,
      },
      {
        field: 'status',
        headerName: 'Status',
        width: 150,
        editable: false,
        valueGetter: (params) => params.row.statement.status,
      },
      {
          field: 'risk_rating_adjusted',
          headerName: 'Criticality',
          width: 150,
          editable: false,
          valueGetter: (params) => params.row.risk_rating_adjusted,
      },
      {
          field: 'created',
          headerName: 'Date Reported',
          width: 150,
          editable: false,
          valueGetter: (params) => moment(params.row.created).format('MM/DD/YYYY'),
      },
      {
          field: 'updated',
          headerName: 'Reported By',
          width: 150,
          editable: false,
          valueGetter: (params) => moment(params.row.updated).format('MM/DD/YYYY'),
      },
    //   {
    //       field: 'comments',
    //       headerName: 'Comments',
    //       width: 150,
    //       editable: false,
    //       valueGetter: (params) => params.row.status,
    //   },
  ]);
  console.log('data: ', data);
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
                        columns={columns}
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