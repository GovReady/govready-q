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
  FormGroup,
  FormControl,
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
      height: "50rem !important",
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

const CustomTextArea = function(props) {
  return (
    <FormGroup controlId="formControlsTextarea">
      <FormControl 
        componentClass="textarea" 
        placeholder="textarea" 
        onChange={(event) => props.onChange(event.target.value)}
        value={props.value}
      />
    </FormGroup>
  );
};

const CustomDisabledTextBox = function(props) {
  return (
    <FormGroup controlId="formControlsTextarea">
      <FormControl 
        type="text" 
        placeholder={props.value}
        value={props.value !== null ? props.value : "-"}
        disabled
        readOnly
      />
    </FormGroup>
  );
};

const schema = {
  title: "",
  type: "object",
  properties: {
    id: {
      type: "integer",
    },
    controls: {
      type: ["string", "null"],
    },
    created: {
      type: ["string", "null"]
    },
    updated: {
      type: ["string", "null"]
    },
    weakness_detection_source: {
      type: ["string", "null"],
      title: "Weakness Detection Source"
    },
    weakness_name: {
      type: ["string", "null"],
      title: "Weakness Name"
    },
    weakness_source_identifier: {
      type: ["string", "null"],
      title: "Weakness Source Identifier"
    },
    poam_id: {
      type: ["integer", "null"],
      title: "Poam Id"
    },
    poam_group: {
      type: ["string", "null"],
      title: "Poam Group"
    },
    milestones: {
      type: ["string", "null"]
    },
    milestone_changes: {
      type: ["string", "null"],
      title: "Milestone Changes"
    },
    remediation_plan: {
      type: ["string", "null"],
      title: "Remediation_plan"
    },
    risk_rating_original: {
      type: ["string", "null"],
      title: "Risk Rating Original"
    },
    risk_rating_adjusted: {
      type: ["string", "null"],
      title: "Risk Rating Adjusted"
    },
    scheduled_completion_date: {
      type: ["string", "null"],
      title: "Scheduled Completion Date"
    },
    extra: {
      title: "",
      type: "object",
      properties: {
        "Monthly Status": {
          type: ["string", "null"],
          enum: [
            "1. Evidence provided to AIS for review", 
            "2. remediated -- completed", 
            "3. in-process -- being worked", 
            "4. Risk Acceptance - waiver", 
            "5. Ad-hob scan & results required", 
            "6. No longer the Sustainment Coordinator", 
            "7. No longer applicable", 
            "8. Not sure how to respond, please schedule a meeting to discuss", 
            "9. Sunset - justification required"
          ]
        },
        "Delay Justification": {
          type: ["string", "null"]
        },
        Comments: {
          type: ["string", "null"],
        },
        "Accepted Risk": {
          type: ["string", "null"]
        },
        "Actual Start Date": {
          type: ["string", "null"]
        },
        "Actual Finish Date": {
          type: ["string", "null"]
        },
        "Assigned Date": {
          type: ["string", "null"]
        },
        "Assigned To": {
          type: ["string", "null"]
        },
        "CSFCategory": {
          type: ["string", "null"]
        },
        "CSFSubCategory": {
          type: ["string", "null"]
        },
        "CSFFunction": {
          type: ["string", "null"]
        },
        Cost: {
          type: ["string", "null"]
        },
        "Days Since Creation": {
          type: ["integer", "null"]
        },
        "Deficiency Category": {
          type: ["string", "null"]
        },
        "Delay Reason": {
          type: ["string", "null"]
        },
        Email: {
          type: ["string", "null"]
        },
        "Number Artifacts": {
          type: ["integer", "null"]
        },
        "Number Milestones": {
          type: ["integer", "null"]
        },
        "POAM Sequence": {
          type: ["integer", "null"]
        },
        "Planned Start Date": {
          type: ["string", "null"]
        },
        "Planned Finish Date": {
          type: ["string", "null"]
        },
        "RBD Approval Date": {
          type: ["string", "null"]
        },
        "Scheduled Completion Date": {
          type: ["string", "null"]
        },
        Severity: {
          type: ["string", "null"]
        },
        "Source of Finding": {
          type: ["string", "null"]
        },
        "User Identified Criticality": {
          type: ["string", "null"]
        },
        Weakness: {
          type: ["string", "null"]
        },
        "Workflow Status": {
          type: ["string", "null"]
        },
        "Workflow Status Date": {
          type: ["string", "null"]
        },
      }
    },
    statement: {
      title: "",
      type: "object",
      properties: {
        body: { 
          type: ["string", "null"]
        },
        created: {
          type: ["string", "null"]
        },
        import_record: {
          type: ["string", "null"],
          title: "Import Record"
        },
        updated: {
          type: ["string", "null"]
        },
        uuid: {
          type: ["string", "null"]
        },
        status: {
          type: ["string", "null"]
        },
        remarks: {
          type: ["string", "null"]
        },
        pid: {
          type: ["string", "null"]
        },
        sid: {
          type: ["string", "null"]
        },
        sid_class: {
          type: ["string", "null"],
          title: "sid class"
        },
        source: {
          type: ["string", "null"]
        },
      }
    }
  }
};
const uiSchema = {
  "ui:widget": CustomDisabledTextBox,
  "ui:options": {
    rows: 5
  },
  "ui:order": [
    "extra", "statement", 
    "controls", "created", "id", "updated", "weakness_detection_source",
    "weakness_name", "weakness_source_identifier", "poam_id", "poam_group", "milestones", 
    "milestone_changes", "remediation_plan", "risk_rating_original", "risk_rating_adjusted", 
    "scheduled_completion_date"
  ],
  
  "created": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox
  },
  "controls": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox
  },
  "id": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox
  },
  "updated": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox
  },
  "weakness_detection_source": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox
  },
  "weakness_name": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox
  }, 
  "weakness_source_identifier": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox
  }, 
  "poam_id": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox
  }, 
  "poam_group": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox
  }, 
  "milestones": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox
  }, 
  "milestone_changes": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox
  }, 
  "remediation_plan": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox
  }, 
  "risk_rating_original": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox
  }, 
  "risk_rating_adjusted": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox
  }, 
  "scheduled_completion_date": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox
  },
  extra: {
    "ui:order": ["Monthly Status", "Delay Justification", "Comments", "Accepted Risk", "Actual Start Date", "Actual Finish Date", "Assigned Date", "Assigned To", "CSFCategory", "CSFSubCategory", "CSFFunction", "Cost", "Days since Creation", "Deficiency Category", "Delay Reason", "Email", "Number Artifacts", "Nnumber Milestones", "POAM Sequence", "Planned Start Date", "Planned Finish Date", "RBD Approval Date", "Scheduled Completion Date", "Severity", "Source of Finding", "User Identified Criticality", "Weakness", "Workflow Status", "Workflow Status Date", "Number Milestones", "Days Since Creation"],
    "ui:widget": CustomDisabledTextBox,
    "ui:readonly": false,

    "Delay Justification": {
      "ui:widget": CustomTextArea
    },
    "Comments": {
      "ui:widget": CustomTextArea
    },
    "Accepted Risk": {
      "ui:readonly": true,
      "ui:widget": CustomDisabledTextBox,
    },
    "Actual Start Date": {
      "ui:readonly": true,
      "ui:widget": CustomDisabledTextBox
    },
    "Actual Finish Date": {
      "ui:readonly": true,
      "ui:widget": CustomDisabledTextBox
    },
    "Assigned Date": {
      "ui:readonly": true,
      "ui:widget": CustomDisabledTextBox,
    },
    "Assigned To": {
      "ui:readonly": true,
      "ui:widget": CustomDisabledTextBox,
    },
    "CSFCategory": {
      "ui:readonly": true,
      "ui:widget": CustomDisabledTextBox,
    },
    "CSFSubCategory": {
      "ui:readonly": true,
      "ui:widget": CustomDisabledTextBox,
    },
    "CSFFunction": {
      "ui:readonly": true,
      "ui:widget": CustomDisabledTextBox,
    },
    "Cost": {
      "ui:readonly": true,
      "ui:widget": CustomDisabledTextBox,
    },
    "Days Since Creation": {
      "ui:readonly": true,
      "ui:widget": CustomDisabledTextBox,
    },
    "Deficiency Category": {
      "ui:readonly": true,
      "ui:widget": CustomDisabledTextBox,
    },
    "Delay Reason": {
      "ui:readonly": true,
      "ui:widget": CustomDisabledTextBox,
    },
    "Email": {
      "ui:readonly": true,
      "ui:widget": CustomDisabledTextBox,
    },
    "Number Artifacts": {
      "ui:readonly": true,
      "ui:widget": CustomDisabledTextBox,
    },
    "Number Milestones": {
      "ui:readonly": true,
      "ui:widget": CustomDisabledTextBox,
    },
    "POAM Sequence": {
      "ui:readonly": true,
      "ui:widget": CustomDisabledTextBox,
    },
    "Planned Start Date": {
      "ui:readonly": true,
      "ui:widget": CustomDisabledTextBox,
    },
    "Planned Finish Date": {
      "ui:readonly": true,
      "ui:widget": CustomDisabledTextBox,
    },
    "RBD Approval Date": {
      "ui:readonly": true,
      "ui:widget": CustomDisabledTextBox,
    },
    "Scheduled Completion Date": {
      "ui:readonly": true,
      "ui:widget": CustomDisabledTextBox,
    },
    "Severity": {
      "ui:readonly": true,
      "ui:widget": CustomDisabledTextBox,
    },
    "Source of Finding": {
      "ui:widget": CustomDisabledTextBox,
      "ui:readonly": true
    },
    "User Identfied Criticality": {
      "ui:readonly": true,
      "ui:widget": CustomDisabledTextBox,
    },
    "Weakness": {
      "ui:readonly": true,
      "ui:widget": CustomDisabledTextBox,
    },
    "Workflow Status": {
      "ui:readonly": true,
      "ui:widget": CustomDisabledTextBox,
    },
    "Workflow Status Date": {
      "ui:readonly": true,
      "ui:widget": CustomDisabledTextBox,
    },
  },
  statement: {
    "ui:widget": CustomDisabledTextBox,
    "ui:order": ["status", "body", "import_record", "updated", "uuid", "remarks", "pid", "sid", "sid_class", "source", "created"],
    "ui:readonly": true,

    "status": {
      "ui:widget": CustomDisabledTextBox,
    },
    "body": {
      "ui:widget": CustomDisabledTextBox,
    },
    "import_record": {
      "ui:widget": CustomDisabledTextBox,
    },
    "updated": {
      "ui:widget": CustomDisabledTextBox,
    },
    "uuid": {
      "ui:widget": CustomDisabledTextBox,
    },
    "remarks": {
      "ui:widget": CustomDisabledTextBox,
    },
    "pid": {
      "ui:widget": CustomDisabledTextBox,
    },
    "sid": {
      "ui:widget": CustomDisabledTextBox,
    },
    "sid_class": {
      "ui:widget": CustomDisabledTextBox,
    },
    "source": {
      "ui:widget": CustomDisabledTextBox,
    },
    "created": {
      "ui:widget": CustomDisabledTextBox,
    }
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
        if(row[field] !== null && typeof row[field] === 'object'){          
          return Object.keys(row[field]).some((secField) => {
            if(row[field][secField] !== null){
              return searchRegex.test(row[field][secField].toString().toLowerCase());
            }
          });
        }
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
            valueGetter: (params) => params.row.weakness_name !== null ? params.row.weakness_name : "-",
          },
          {
            field: 'status',
            headerName: 'Status',
            width: 150,
            editable: false,
            valueGetter: (params) => params.row.statement.status !== null ? params.row.statement.status : "-",
          },
          {
              field: 'risk_rating_adjusted',
              headerName: 'Criticality',
              width: 150,
              editable: false,
              valueGetter: (params) => params.row.risk_rating_adjusted !== null ? params.row.risk_rating_adjusted : "-",
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
        newColumns.push({
          field: key,
          headerName: key,
          width: 150,
          editable: ["Delay Justification", "Status as of June", "Comments"].includes(key) ? true : false,
          valueGetter: (params) => params.row.extra[key] !== null ? params.row.extra[key] : "-"
        })
      }
      setColumns(newColumns)
    });
  }, []);

  const onSubmit = async ({formData}, e) => {
    // 1. PUT update to POAM to DB
    const updatePOAM = await axios.put(`/api/v2/systems/${systemId}/poams/${formData.id}/updatePoamExtra/`, { update: formData.extra });
    if(updatePOAM.status === 200){
      // window.location.reload();
      // 2. Update current instance on page
      const updatedRows = rows.map((row) => {
        if (row.id === formData.id) {
          return formData;
        } else {
          return row;
        }
      });
      setRows(updatedRows);
      handleClose();
    } else {
      console.error("Something went wrong in creating and appointing new appointments")
    }
  };

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
                        pageSize={12}
                        rowsPerPageOptions={[12]}
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
                      dialogClassName={"poam-edit-modal"}
                      show={openEditPoamModal}
                      hide={() => setOpenEditPoamModal(false)}
                      header={
                        <span>Update POAM {currentPoam.id}: {currentPoam.weakness_name}</span>
                      }
                      body={
                        <div>
                          <Form 
                            schema={schema} 
                            uiSchema={uiSchema}
                            formData={currentPoam}
                            onSubmit={onSubmit}
                          />
                        </div>
                      }
                      bodyStyle={
                        {
                          height: "75rem",
                          overflowY: "scroll" 
                        }
                      }
                    />
              </div>
          </Grid>
      </div>
  )
}