import React, { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import PropTypes from 'prop-types';
import axios from 'axios';
import moment from 'moment';
import { 
  DataGrid, 
  GridToolbar, 
  useGridApiContext,
} from '@mui/x-data-grid';
// import {
//   DataGrid,
//   escapeRegExp,
//   GridToolbarDensitySelector,
//   GridToolbarFilterButton,
// } from '@material-ui/data-grid';
import { v4 as uuid_v4 } from "uuid";
import { 
  Chip,
  Grid,
  IconButton,
  Select,
  Stack,
  TextField,
} from '@mui/material';
// import { createMuiTheme } from '@material-ui/core/styles';
import { makeStyles } from '@mui/styles';
import ClearIcon from '@mui/icons-material/Clear';
import SearchIcon from '@mui/icons-material/Search';
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
// const defaultTheme = createMuiTheme();

// const searchStyles = makeStyles({
//     root: {
//       padding: theme.spacing(0.5, 0.5, 0),
//       justifyContent: 'space-between',
//       display: 'flex',
//       alignItems: 'flex-start',
//       flexWrap: 'wrap',
//     },
//     textField: {
//       [theme.breakpoints.down('xs')]: {
//         width: '100%',
//       },
//       margin: theme.spacing(1, 0.5, 1.5),
//       '& .MuiSvgIcon-root': {
//         marginRight: theme.spacing(0.5),
//       },
//       '& .MuiInput-underline:before': {
//         borderBottom: `1px solid ${theme.palette.divider}`,
//       },
//     },
//   }
// );

function QuickSearchToolbar(props) {
  // const classes = searchStyles();

  return (
    <div style={{ float: 'right' }}>
      <TextField
        variant="standard"
        value={props.value}
        onChange={props.onChange}
        placeholder="Search…"
        InputProps={{
          startAdornment: <SearchIcon fontSize="large" />,
          endAdornment: (
            <IconButton
              title="Clear"
              aria-label="Clear"
              size="large"
              style={{ visibility: props.value ? 'visible' : 'hidden' }}
              onClick={props.clearSearch}
            >
              <ClearIcon />
            </IconButton>
          ),
        }}
        sx={{ 
          marginBottom: '1rem', 
          input: { 
            fontSize: '18px',
          } 
        }}
      />
    </div>
  );
}

QuickSearchToolbar.propTypes = {
  clearSearch: PropTypes.func.isRequired,
  onChange: PropTypes.func.isRequired,
  value: PropTypes.string.isRequired,
};

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
  const [ rows, setRows ] = useState(data)
  const [ searchText, setSearchText ] = useState('');

  function escapeRegex(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }
  const requestSearch = (searchValue) => {
    setSearchText(searchValue);
    const searchRegex = new RegExp(escapeRegex(searchValue.toLowerCase()));
    
    const filteredRows = data.filter((row) => {
      return Object.keys(row).some((field) => {
        if(row[field] !== null){
          return searchRegex.test(row[field].toString().toLowerCase());
        }
      });
    });
    setRows(filteredRows);
  };

  useEffect(() => {
    setRows(data);
  }, [data]);

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
  return (
      <div style={{ maxHeight: '2000px', width: '100%' }}>  
          <Grid className="poc-data-grid" sx={{ minHeight: '500px' }}>
              <div style={{width: "calc(100% - 1rem - 25px)", marginTop: "1rem" }}>
                <QuickSearchToolbar value={searchText} onChange={(event) => requestSearch(event.target.value)} clearSearch={() => requestSearch('')}/>
                  <div style={{ width: "100%", marginBottom: "1rem", display: "flex", justifyContent: "space-between" }}>
                      <DataGrid
                        className={dgClasses.root}
                        autoHeight={true}
                        density="compact"
                        rows={rows}
                        columns={columns}
                        pageSize={25}
                        rowsPerPageOptions={[25]}
                        rowHeight={50}
                        checkboxSelection
                        // components={{ Toolbar: QuickSearchToolbar }}
                        // componentsProps={{
                        //   toolbar: {
                        //     value: searchText,
                        //     onChange: (event) => requestSearch(event.target.value),
                        //     clearSearch: () => requestSearch(''),
                        //   },
                        // }}
                        // components={{
                        //   Toolbar: GridToolbar,
                        // }}
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