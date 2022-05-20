import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
import { DataGrid } from '@mui/x-data-grid';
import {
  Button,
  IconButton,
  Grid,
  TextField,
} from '@mui/material';
import { makeStyles } from '@mui/styles';
import SelectUnstyled, { selectUnstyledClasses } from '@mui/base/SelectUnstyled';
import OptionUnstyled, { optionUnstyledClasses } from '@mui/base/OptionUnstyled';
import PopperUnstyled from '@mui/base/PopperUnstyled';
import { styled } from '@mui/system';
import ClearIcon from '@mui/icons-material/Clear';
import SearchIcon from '@mui/icons-material/Search';

const blue = {
  100: '#DAECFF',
  200: '#99CCF3',
  400: '#3399FF',
  500: '#007FFF',
  600: '#0072E5',
  900: '#003A75',
};

const grey = {
  100: '#E7EBF0',
  200: '#E0E3E7',
  300: '#CDD2D7',
  400: '#B2BAC2',
  500: '#A0AAB4',
  600: '#6F7E8C',
  700: '#3E5060',
  800: '#2D3843',
  900: '#1A2027',
};

const StyledButton = styled('button')(
  ({ theme }) => `
  font-family: IBM Plex Sans, sans-serif;
  font-size: 0.875rem;
  box-sizing: border-box;
  min-height: calc(1.5em + 22px);
  min-width: 130px;
  background: ${theme.palette.mode === 'dark' ? grey[900] : '#fff'};
  border: 1px solid ${theme.palette.mode === 'dark' ? grey[800] : grey[300]};
  border-radius: 0.75em;
  margin: 0.5em;
  padding: 10px;
  text-align: left;
  line-height: 1.5;
  color: ${theme.palette.mode === 'dark' ? grey[300] : grey[900]};

  &:hover {
    background: ${theme.palette.mode === 'dark' ? '' : grey[100]};
    border-color: ${theme.palette.mode === 'dark' ? grey[700] : grey[400]};
  }

  &.${selectUnstyledClasses.focusVisible} {
    outline: 3px solid ${theme.palette.mode === 'dark' ? blue[600] : blue[100]};
  }

  &.${selectUnstyledClasses.expanded} {
    &::after {
      content: '▴';
    }
  }

  &::after {
    content: '▾';
    float: right;
  }
  `,
);

const StyledListbox = styled('ul')(
  ({ theme }) => `
  font-family: IBM Plex Sans, sans-serif;
  font-size: 0.875rem;
  box-sizing: border-box;
  padding: 5px;
  margin: 10px 0;
  min-width: 320px;
  background: ${theme.palette.mode === 'dark' ? grey[900] : '#fff'};
  border: 1px solid ${theme.palette.mode === 'dark' ? grey[800] : grey[300]};
  border-radius: 0.75em;
  color: ${theme.palette.mode === 'dark' ? grey[300] : grey[900]};
  overflow: auto;
  outline: 0px;
  `,
);

const StyledOption = styled(OptionUnstyled)(
  ({ theme }) => `
  list-style: none;
  padding: 8px;
  border-radius: 0.45em;
  cursor: default;

  &:last-of-type {
    border-bottom: none;
  }

  &.${optionUnstyledClasses.selected} {
    background-color: ${theme.palette.mode === 'dark' ? blue[900] : blue[100]};
    color: ${theme.palette.mode === 'dark' ? blue[100] : blue[900]};
  }

  &.${optionUnstyledClasses.highlighted} {
    background-color: ${theme.palette.mode === 'dark' ? grey[800] : grey[100]};
    color: ${theme.palette.mode === 'dark' ? grey[300] : grey[900]};
  }

  &.${optionUnstyledClasses.highlighted}.${optionUnstyledClasses.selected} {
    background-color: ${theme.palette.mode === 'dark' ? blue[900] : blue[100]};
    color: ${theme.palette.mode === 'dark' ? blue[100] : blue[900]};
  }

  &.${optionUnstyledClasses.disabled} {
    color: ${theme.palette.mode === 'dark' ? grey[700] : grey[400]};
  }

  &:hover:not(.${optionUnstyledClasses.disabled}) {
    background-color: ${theme.palette.mode === 'dark' ? grey[800] : grey[100]};
    color: ${theme.palette.mode === 'dark' ? grey[300] : grey[900]};
  }
  `,
);

const StyledPopper = styled(PopperUnstyled)`
  z-index: 1;
`;

const CustomSelect = React.forwardRef(function CustomSelect(props, ref) {
  const components = {
    Root: StyledButton,
    Listbox: StyledListbox,
    Popper: StyledPopper,
    ...props.components,
  };

  return <SelectUnstyled {...props} ref={ref} components={components} />;
});

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
  const dgClasses = datagridStyles();
  const [data, setData] = useState([]);
  const [rows, setRows] = useState(data)
  const [sortby, setSortBy] = useState(["name", "asc"]);
  const [searchText, setSearchText] = useState('');
  const [columnsForEditor, setColumnsForEditor] = useState([]);
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
  function escapeRegex(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }
  const requestSearch = (searchValue) => {
    setSearchText(searchValue);
    const searchRegex = new RegExp(escapeRegex(searchValue.toLowerCase()));
    
    const filteredRows = data.filter((row) => {
      return Object.keys(row).some((field) => {
        if(row[field] !== null){
          if(field === 'system'){
            return searchRegex.test(row[field].name.toString().toLowerCase());
          }
          return searchRegex.test(row[field].toString().toLowerCase());
        }
      });
    });
    setRows(filteredRows);
  };

  const handleChange = (event, params, data) => {
    const updatedData = [...data];
    updatedData[params.row.id-1].status = event;
    setData(updatedData);
  }
  const handleSubmit = async (params) => {
    const updatedRequest = {
      user: params.row.userId,
      system: params.row.system.id,
      requested_element: params.row.requested_element.id,
      criteria_comment: params.row.criteria_comment,
      criteria_reject_comment: params.row.criteria_reject_comment,
      status: params.row.status,
    }
    const updateRequestResponse = await axios.put(`/api/v2/requests/${params.row.requestId}/`, updatedRequest);
    if(updateRequestResponse.status === 200){
      
    } else {
      console.error("Something went wrong in creating and setting new request to element");
    }
  }
  
  useEffect(() => {
    axios(`/api/v2/elements/${elementId}/retrieveRequests/`).then(response => {
      setData(response.data.requested);
    });
  }, []);

  useEffect(() => {
    const newData = data.filter((item) => item.status != "Closed")
    setRows(newData);
  }, [data]);

  useEffect(() => {
    setColumnsForEditor([
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
        editable: true,
        type: 'text',
        renderCell: (params) => (
          <Grid container rowSpacing={1} columnSpacing={{ xs: 1, sm: 2, md: 3 }}>
            {data.length !== 0 && <Grid item xs={6}>
                <CustomSelect value={params.row.status} onChange={(event) => handleChange(event, params, data)}>
                  <StyledOption value={"Open"}>Open</StyledOption>
                  <StyledOption value={"Pending"}>Pending</StyledOption>
                  <StyledOption value={"In Progress"}>In Progress</StyledOption>
                  <StyledOption value={"Approve"}>Approve</StyledOption>
                  <StyledOption value={"Reject"}>Reject</StyledOption>
                  <StyledOption value={"Closed"}>Closed</StyledOption>
                </CustomSelect>
            </Grid>}
            <Grid item xs={6}>
              <Button variant="primary" onClick={() => handleSubmit(params)}>Submit</Button>
            </Grid>
          </Grid>
        ),
      },
    ]);
  }, [data])

  return (
      <div style={{ maxHeight: '2000px', width: '100%' }}>
          {data !== null && columnsForEditor.length !== 0 && <Grid className="poc-data-grid" sx={{ minHeight: '500px' }}>
          <QuickSearchToolbar value={searchText} onChange={(event) => requestSearch(event.target.value)} clearSearch={() => requestSearch('')}/>
              <div style={{width: "calc(100% - 1rem - 25px)", marginTop: "1rem" }}>
                  <div style={{ width: "100%", marginBottom: "1rem", display: "flex", justifyContent: "space-between" }}>
                      <DataGrid
                        className={dgClasses.root}
                        autoHeight={true}
                        density="compact"
                        rows={rows}
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
          }
      </div>
  )
}