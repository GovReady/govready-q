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
  Row,
  Modal
} from 'react-bootstrap';
import Form from "@rjsf/core";
import { AsyncPagination } from "../shared/asyncTypeahead";
import { red, green } from '@mui/material/colors';
import { ReactModal } from '../shared/modal';
import { hide, show } from '../shared/modalSlice';
function QuickSearchToolbar(props) {

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
      // overflowX: "scroll",
    },
    // "& .MuiDataGrid-virtualScroller":{
    //   height: "30rem !important",
    // }
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
  },
  leftColumn: {
    position: '-webkit-sticky',
    position: 'sticky',
  }
});

// const JForm = JSONSchemaForm.default;

const schema = {
  title: "Test form",
  type: "object",
  properties: {
    id: {
      type: "string",
    },
    controls: {
      type: "string",
    },
    created: {
      type: "string"
    },
    updated: {
      type: "string"
    },
    weakness_detection_source: {
      type: "string",
      title: "Weakness Detection Source"
    },
    weakness_name: {
      type: "string",
      title: "Weakness Name"
    },
    weakness_source_identifier: {
      type: "string",
      title: "Weakness Source Identifier"
    },
    poam_id: {
      type: "string",
      title: "Poam Id"
    },
    poam_group: {
      type: "string",
      title: "Poam Group"
    },
    milestones: {
      type: "string"
    },
    milestone_changes: {
      type: "string",
      title: "Milestone Changes"
    },
    remediation_plan: {
      type: "string",
      title: "Remediation_plan"
    },
    risk_rating_original: {
      type: "string",
      title: "Risk Rating Original"
    },
    risk_rating_adjusted: {
      type: "string",
      title: "Risk Rating Adjusted"
    },
    scheduled_completion_date: {
      type: "string",
      title: "Scheduled Completion Date"
    },
    extra: {
      title: "",
      type: "object",
      properties: {
        "Accepted Risk": {
          type: "string"
        },
        "Actual Start Date": {
          type: "string"
        },
        "Actual Finish Date": {
          type: "string"
        },
        "Assigned Date": {
          type: "string"
        },
        "Assigned To": {
          type: "string"
        },
        "CSFCategory": {
          type: "string"
        },
        "CSFSubCategory": {
          type: "string"
        },
        "CSFFunction": {
          type: "string"
        },
        Comments: {
          type: "string",
        },
        Cost: {
          type: "string"
        },
        "Days Since Creation": {
          type: "string"
        },
        "Deficiency Category": {
          type: "string"
        },
        "Delay Justification": {
          type: "string"
        },
        "Delay Reason": {
          type: "string"
        },
        Email: {
          type: "string"
        },
        "Number Artifacts": {
          type: "string"
        },
        "Number Milestones": {
          type: "string"
        },
        "POAM Sequence": {
          type: "string"
        },
        "Planned Start Date": {
          type: "string"
        },
        "Planned Finish Date": {
          type: "string"
        },
        "RBD Approval Date": {
          type: "string"
        },
        "Scheduled Completion Date": {
          type: "string"
        },
        Severity: {
          type: "string"
        },
        "Source of Finding": {
          type: "string"
        },
        "Status as of June": {
          type: "string",
        },
        "User Identified Criticality": {
          type: "string"
        },
        Weakness: {
          type: "string"
        },
        "Workflow Status": {
          type: "string"
        },
        "Workflow Status Date": {
          type: "string"
        },
      }
    },
    statement: {
      title: "",
      type: "object",
      properties: {
        body: { 
          type: "string"
        },
        created: {
          type: "string"
        },
        import_record: {
          type: "string",
          title: "Import Record"
        },
        updated: {
          type: "string"
        },
        uuid: {
          type: "string"
        },
        status: {
          type: "string"
        },
        remarks: {
          type: "string"
        },
        pid: {
          type: "string"
        },
        sid: {
          type: "string"
        },
        sid_class: {
          type: "string",
          title: "sid class"
        },
        source: {
          type: "string"
        },
      }
    }
  }
};
const uiSchema = {
  "ui:widget": "textarea",
  "ui:options": {
    rows: 5
  },
  "ui:order": [
    "extra", 
    "statement", "controls", "created", "id", "updated", "weakness_detection_source",
    "weakness_name", "weakness_source_identifier", "poam_id", "poam_group", "milestones", 
    "milestone_changes", "remediation_plan", "risk_rating_original", "risk_rating_adjusted", 
    "scheduled_completion_date"],
  "created": {
    "ui:readonly": true
  },
  "controls": {
    "ui:readonly": true
  },
  "id": {
    "ui:readonly": true
  },
  "updated": {
    "ui:readonly": true
  },
  "weakness_detection_source": {
    "ui:readonly": true
  },
  "weakness_name": {
    "ui:readonly": true
  }, 
  "weakness_source_identifier": {
    "ui:readonly": true
  }, 
  "poam_id": {
    "ui:readonly": true
  }, 
  "poam_group": {
    "ui:readonly": true
  }, 
  "milestones": {
    "ui:readonly": true
  }, 
  "milestone_changes": {
    "ui:readonly": true
  }, 
  "remediation_plan": {
    "ui:readonly": true
  }, 
  "risk_rating_original": {
    "ui:readonly": true
  }, 
  "risk_rating_adjusted": {
    "ui:readonly": true
  }, 
  "scheduled_completion_date": {
    "ui:readonly": true
  },
  extra: {
    "ui:order": ["Delay Justification", "Status as of June", "Comments", "Accepted Risk", "Actual Start Date", "Actual Finish Date", "Assigned Date", "Assigned To", "CSFCategory", "CSFSubCategory", "CSFFunction", "Cost", "Days since Creation", "Deficiency Category", "Delay Reason", "Email", "Number Artifacts", "Nnumber Milestones", "POAM Sequence", "Planned Start Date", "Planned Finish Date", "RBD Approval Date", "Scheduled Completion Date", "Severity", "Source of Finding", "User Identified Criticality", "Weakness", "Workflow Status", "Workflow Status Date", "Number Milestones", "Days Since Creation"],
    "ui:readonly": false,
    "Accepted Risk": {
      "ui:readonly": true
    },
    "Actual Start Date": {
      "ui:readonly": true
    },
    "Actual Finish Date": {
      "ui:readonly": true
    },
    "Assigned Date": {
      "ui:readonly": true
    },
    "Assigned To": {
      "ui:readonly": true
    },
    "CSFCategory": {
      "ui:readonly": true
    },
    "CSFSubCategory": {
      "ui:readonly": true
    },
    "CSFFunction": {
      "ui:readonly": true
    },
    "Cost": {
      "ui:readonly": true
    },
    "Days Since Creation": {
      "ui:readonly": true
    },
    "Deficiency Category": {
      "ui:readonly": true
    },
    "Delay Reason": {
      "ui:readonly": true
    },
    "Email": {
      "ui:readonly": true
    },
    "Number Artifacts": {
      "ui:readonly": true
    },
    "Number Milestones": {
      "ui:readonly": true
    },
    "POAM Sequence": {
      "ui:readonly": true
    },
    "Planned Start Date": {
      "ui:readonly": true
    },
    "Planned Finish Date": {
      "ui:readonly": true
    },
    "RBD Approval Date": {
      "ui:readonly": true
    },
    "Scheduled Completion Date": {
      "ui:readonly": true
    },
    "Severity": {
      "ui:readonly": true
    },
    "Source of Finding": {
      "ui:readonly": true
    },
    "User Identfied Criticality": {
      "ui:readonly": true
    },
    "Weakness": {
      "ui:readonly": true
    },
    "Workflow Status": {
      "ui:readonly": true
    },
    "Workflow Status Date": {
      "ui:readonly": true
    },
  },
  statement: {
    "ui:order": ["status", "body", "import_record", "updated", "uuid", "remarks", "pid", "sid", "sid_class", "source", "created"],
    "ui:readonly": true,
  },
  
  
};

export const SystemSummary = ({ systemId, projectId }) => {
  const dispatch = useDispatch();

  const classes = useStyles();
  const dgClasses = datagridStyles();
  const [data, setData] = useState([]);
  const [sortby, setSortBy] = useState(["name", "asc"]);
  const [ rows, setRows ] = useState(data)
  const [ searchText, setSearchText ] = useState('');
  const [columns, setColumns] = useState([]);

  const [openEditPoamModal, setOpenEditPoamModal] = useState(false);
  const [currentPoam, setCurrentPoam] = useState({})
  
  
  const handleClose = () => {
    setOpenEditPoamModal(false);
  }
  
  const handleOpenIndividualPoam = (row) => {
    setOpenEditPoamModal(true);
    setCurrentPoam(row);
  }

  function escapeRegex(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  const isObjectEmpty = (obj) => {
    return Object.keys(obj).length === 0;
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
      
      // if (!isObjectEmpty(response.data.data[0].extra)) {
        
      // }
      const newColumns = [
        {
            field: 'weakness_name',
            headerName: 'POA&M',
            width: 150,
            editable: false,
            hideable: false,
            // valueGetter: (params) => params.row.weakness_name,
            renderCell: (params) => (
              <div className={classes.leftColumn} onClick={(e) => {
                  e.stopPropagation();
                  e.preventDefault();
                  handleOpenIndividualPoam(params.row)
                }
              }>
                {params.row.weakness_name}
              </div>
            )
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
      ];
      for (const [key, value] of Object.entries(response.data.data[0].extra)) {
        // console.log(`${key}: ${value}`);
        newColumns.push({
          field: key,
          headerName: key,
          width: 150,
          editable: ["Delay Justification", "Status as of June", "Comments"].includes(key) ? true : false,
          valueGetter: (params) => params.row.extra[key]
        })
      }
      setColumns(newColumns)
    });
  }, [])

  // const createFormControl = (obj) => {
  //   Object.entries(obj).map(([key, value], index) => {
  //     if (typeof(value) !== 'object') {
  //       // console.log(`not object => key: ${key} value: ${value} at index: ${index}`)
  //       return (
  //         <p key={index}>{key}</p>
  //       )
  //     } 
  //     else if(value === null){
  //       // console.log(`null => key: ${key} value: ${value} at index: ${index}`)
  //       return (
  //         <p key={index}>{key}</p>
  //       )
  //     }
  //     else {
  //       createFormControl(value)
  //     }
  //   })
  // }


  return (
      <div style={{ maxHeight: '2000px', width: '100%' }}>  
          <Grid className="poc-data-grid" sx={{ minHeight: '500px' }}>
              <div style={{width: "calc(100% - 1rem - 25px)", marginTop: "1rem" }}>
                <QuickSearchToolbar value={searchText} onChange={(event) => requestSearch(event.target.value)} clearSearch={() => requestSearch('')}/>
                  <div style={{ width: "100%", marginBottom: "1rem", display: "flex", justifyContent: "space-between" }}>
                      <DataGrid
                        className={dgClasses.root}
                        // autoHeight={true}
                        density="compact"
                        rows={rows}
                        columns={columns}
                        pageSize={25}
                        rowsPerPageOptions={[25]}
                        rowHeight={50}
                        checkboxSelection
                        showScrollbar={true}
                        selectRow
                        initialState={{
                          pinnedColumns: {
                            left: ['weakness_name'],
                            // right: ['Delay Justification', 'Status as of June', 'Comments']
                          }
                          // columns: {
                          //   columnVisibilityModel: {
                          //     // Hide columns status and traderName, the other columns will remain visible
                          //     evidence: false,
                          //     status: false,
                          //     risk_rating_adjusted: false,
                          //     created: false,
                          //     updated: false,
                          //     "Assigned To": false,
                          //     "User Identified Criticality": false,
                          //     "Workflow Status Date": false,
                          //     "Scheduled Completion Date": false,
                          //     "Planned Start Date": false,
                          //     "Planned Finish Date": false,
                          //     "Actual Finish Date": false,
                          //     "Deficiency Category": false,
                          //     "Days Since Creation": false,
                          //     "Source of Finding": false,
                          //     "RBD Approval Date": false,
                          //     "Actual Start Date": false,
                          //     "Number Milestones": false,
                          //     "Number Artifacts": false,
                          //     "Workflow Status": false,
                          //     "CSFSubCategory": false,
                          //     "CSFFunction": false,
                          //     "CSFCategory": false,
                          //     "Delay Reason": false,
                          //     "Accepted Risk": false,
                          //     "Assigned Date": false,
                          //     "POAM Sequence": false,
                          //     "Weakness": false,
                          //   }
                          // },
                          
                        }}
                        
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
                  <ReactModal
                      title={`Edit POAM`}
                      show={openEditPoamModal}
                      hide={() => setOpenEditPoamModal(false)}
                      header={
                        <span>header{console.log(currentPoam)}</span>
                      }
                      body={
                        <div style={{ height: '80%', overflowY: "scroll" }}>
                          <Form 
                            schema={schema} 
                            uiSchema={uiSchema}
                            formData={currentPoam}
                          />
                        </div>
                      }
                      />
              </div>
          </Grid>
      </div>
  )
}