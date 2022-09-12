import React, { useEffect, useState, useRef } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import PropTypes from 'prop-types';
import axios from 'axios';
import moment from 'moment';
import clsx from 'clsx';

import { 
  DataGrid, 
  GridToolbar, 
  useGridApiContext,
  GridToolbarContainer,
  GridToolbarExport 
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
// import Form from "@rjsf/core"; 
import Form from "react-jsonschema-form";

import LayoutField from '../shared/schemaForm'

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
};

const CustomToolbar = () => {
  return (
    <GridToolbarContainer>
      <GridToolbarExport csvOptions={{ allColumns: true }} />
    </GridToolbarContainer>
  )
};

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
    '& .super-app-theme--cell': {
      backgroundColor: 'rgba(224, 183, 60, 0.55)',
      color: '#1a3e72',
      fontWeight: '600',
    },

    '& .super-app.critical': {
      backgroundColor: '#ff9999',
    },
    '& .super-app.advice': {
      backgroundColor: '#ffdc9b',
    },
    '& .super-app.target': {
      backgroundColor: '#81ff81',
    },
    '& .super-app.closure': {
      backgroundColor: '#ba9af5',
    },
    '& .super-app.followup': {
      backgroundColor: '#7bddff',
    },
    '& .super-app.new': {
      backgroundColor: 'peachpuff',
      // color: '#1a3e72',
      // fontWeight: '600',
    },
    '& .super-app.default': {
      backgroundColor: '#d47483',
      // color: '#1a3e72',
      // fontWeight: '600',
    },
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
    '&:hover': {
      textDecoration: 'underline',
      cursor: 'pointer'
    }
  },
  critical: {
    backgroundColor: "red",
    height: '100%',
    width: '100%',
  },
  advise: {
    backgroundColor: "orange",
    height: '100%',
    width: '100%',
  },
  target: {
    backgroundColor: "green",
    height: '100%',
    width: '100%',
  },
  closure: {
    backgroundColor: "purple",
    height: '100%',
    width: '100%',
  },
  followup: {
    backgroundColor: "blue",
    height: '100%',
    width: '100%',
  },
  new: {
    backgroundColor: "peachpuff",
    height: '100%',
    width: '100%',
  },
  normal: {
    backgroundColor: "grey",
    height: '100%',
    width: '100%',
  }
});

// const JForm = JSONSchemaForm.default;

const CustomTextArea = function(props) {
  return (
    <FormGroup controlId="formControlsTextarea">
      <FormControl 
        componentClass="textarea" 
        placeholder="" 
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
      title: "Controls"
    },
    created: {
      type: ["string", "null"],
      title: "Created"
    },
    updated: {
      type: ["string", "null"],
      title: "Updated"
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
      type: ["string", "null"],
      title: "Milestones"
    },
    milestone_changes: {
      type: ["string", "null"],
      title: "Milestone Changes"
    },
    remediation_plan: {
      type: ["string", "null"],
      title: "Remediation Plan"
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
    "extra__Monthly Status": {
      type: ["string", "null"],
      title: "Monthly Status",
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
    "extra__Delay Justification": {
      type: ["string", "null"],
      title: "Delay Justification",
    },
    "extra__Comments": {
      type: ["string", "null"],
      title: "Comments",
    },
    "extra__Accepted Risk": {
      type: ["string", "null"],
      title: "Accepted Risk"
    },
    "extra__Actual Start Date": {
      type: ["string", "null"],
      title: "Actual Start Date"
    },
    "extra__Actual Finish Date": {
      type: ["string", "null"],
      title: "Actual Finish Date"
    },
    "extra__Assigned Date": {
      type: ["string", "null"],
      title: "Assigned Date"
    },
    "extra__Assigned To": {
      type: ["string", "null"],
      title: "Assigned To"
    },
    "extra__CSFCategory": {
      type: ["string", "null"],
      title: "CSFCategory"
    },
    "extra__CSFSubCategory": {
      type: ["string", "null"],
      title: "CSFSubCategory"
    },
    "extra__CSFFunction": {
      type: ["string", "null"],
      title: "CSFFunction"
    },
    "extra__Cost": {
      type: ["string", "null"],
      title: "Cost"
    },
    "extra__Days Since Creation": {
      type: ["integer", "null"],
      title: "Days Since Creation"
    },
    "extra__Deficiency Category": {
      type: ["string", "null"],
      title: "Deficiency Category"
    },
    "extra__Delay Reason": {
      type: ["string", "null"],
      title: "Delay Reason"
    },
    "extra__Email": {
      type: ["string", "null"],
      title: "Email"
    },
    "extra__Number Artifacts": {
      type: ["integer", "null"],
      title: "Number Artifacts"
    },
    "extra__Number Milestones": {
      type: ["integer", "null"],
      title: "Number Milestones"
    },
    "extra__POAM Sequence": {
      type: ["integer", "null"],
      title: "POAM Sequence"
    },
    "extra__Planned Start Date": {
      type: ["string", "null"],
      title: "Planned Start Date"
    },
    "extra__Planned Finish Date": {
      type: ["string", "null"],
      title: "Planned Finish Date"
    },
    "extra__RBD Approval Date": {
      type: ["string", "null"],
      title: "RBD Approval Date"
    },
    "extra__Scheduled Completion Date": {
      type: ["string", "null"],
      title: "Scheduled Completion Date"
    },
    "extra__Severity": {
      type: ["string", "null"],
      title: "Severity"
    },
    "extra__Source of Finding": {
      type: ["string", "null"],
      title: "Source of Finding"
    },
    "extra__User Identified Criticality": {
      type: ["string", "null"],
      title: "User Identified Criticality"
    },
    "extra__Weakness": {
      type: ["string", "null"],
      title: "Weakness"
    },
    "extra__Workflow Status": {
      type: ["string", "null"],
      title: "Workflow Status"
    },
    "extra__Workflow Status Date": {
      type: ["string", "null"],
      title: "Workflow Status Date"
    },
    "extra__Days Until Auto-Approved": {
      type: ["string", "null"],
      title: "Days Until Auto-Approved"
    },
    "extra__Control Risk Severity": {
      type: ["string", "null"],
      title: "Control Risk Severity"
    },

    "statement__body": { 
      type: ["string", "null"],
      title: "Body"
    },
    "statement__created": {
      type: ["string", "null"],
      title: "Created"
    },
    "statement__import_record": {
      type: ["string", "null"],
      title: "Import Record"
    },
    "statement__updated": {
      type: ["string", "null"],
      title: "Updated"
    },
    "statement__uuid": {
      type: ["string", "null"],
      title: "UUID"
    },
    "statement__status": {
      type: ["string", "null"],
      title: "Status"
    },
    "statement__remarks": {
      type: ["string", "null"],
      title: "Remarks"
    },
    "statement__pid": {
      type: ["string", "null"],
      title: "PID"
    },
    "statement__sid": {
      type: ["string", "null"],
      title: "SID"
    },
    "statement__sid_class": {
      type: ["string", "null"],
      title: "SID Class"
    },
    "statement__source": {
      type: ["string", "null"],
      title: "Source"
    }
  }
}



export const TitleField = (props) => {
  const { title, required, id } = props

  let legend = legend = `${title}${(required ? '*' : '')}`
  return <label className="control-label" htmlFor={id}>{legend}</label>
}

const fields = {
  layout_grid: LayoutField,
  TitleField: TitleField
}

const isFilled = (fieldName) => ({ formData }) => (formData[fieldName] && formData[fieldName].length) ? true : false
const isTrue = (fieldName) => ({ formData }) => (formData[fieldName])

const uiSchema = {
  'ui:field': 'layout_grid',
  'ui:layout_grid': { 'ui:row': [
    { 'ui:col': { xs: 12, children: [
      
      { 'ui:group': '','ui:row': [
        { 'ui:col': { md: 12, children: ['extra__Monthly Status'] } },
        { 'ui:col': { md: 12, children: ['extra__Delay Justification'] } },
        { 'ui:col': { md: 12, children: ['extra__Comments'] } },
      ] },

      { 'ui:group': '', 'ui:row': [
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['weakness_name'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['poam_id'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['id'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['controls'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['created'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['updated'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['weakness_detection_source'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['weakness_name'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['weakness_source_identifier'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['poam_group'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['milestones'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['milestone_changes'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['remediation_plan'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['risk_rating_original'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['risk_rating_adjusted'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['scheduled_completion_date'] } },
      ] },

      { 'ui:group': '', 'ui:row': [
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['extra__Accepted Risk'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['extra__Actual Start Date'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['extra__Actual Finish Date'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['extra__Assigned Date'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['extra__Assigned To'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['extra__CSFCategory'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['extra__CSFSubCategory'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['extra__CSFFunction'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['extra__Cost'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['extra__Days since Creation'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['extra__Deficiency Category'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['extra__Delay Reason'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['extra__Email'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['extra__Number Artifacts'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['extra__Number Milestones'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['extra__POAM Sequence'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['extra__Planned Start Date'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['extra__Planned Finish Date'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['extra__RBD Approval Date'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['extra__Scheduled Completion Date'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['extra__Severity'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['extra__Source of Finding'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['extra__User Identified Criticality'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['extra__Weakness'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['extra__Workflow Status'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['extra__Workflow Status Date'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['extra__Number Milestones'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['extra__Days Since Creation'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['extra__Days Until Auto-Approved'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['extra__Control Risk Severity'] } },
      ] },
      { 'ui:group': '', 'ui:row': [
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['statement__status'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['statement__body'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['statement__import_record'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['statement__updated'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['statement__uuid'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['statement__remarks'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['statement__pid'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['statement__sid'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['statement__sid_class'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['statement__source'] } },
        { 'ui:col': { sm: 3, md: 3, lg: 3, children: ['statement__created'] } },

      ] },
    ] } },
  ] },
  'extra__Delay Status': {
    'autofocus': true,
  },
  'extra__Delay Justification': {
    'ui:widget': CustomTextArea
  },
  'extra__Comments': {
    'ui:widget': CustomTextArea
  },

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


  "extra__Accepted Risk": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox,
  },
  "extra__Actual Start Date": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox
  },
  "extra__Actual Finish Date": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox
  },
  "extra__Assigned Date": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox,
  },
  "extra__Assigned To": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox,
  },
  "extra__CSFCategory": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox,
  },
  "extra__CSFSubCategory": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox,
  },
  "extra__CSFFunction": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox,
  },
  "extra__Cost": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox,
  },
  "extra__Days Since Creation": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox,
  },
  "extra__Deficiency Category": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox,
  },
  "extra__Delay Reason": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox,
  },
  "extra__Email": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox,
  },
  "extra__Number Artifacts": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox,
  },
  "extra__Number Milestones": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox,
  },
  "extra__POAM Sequence": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox,
  },
  "extra__Planned Start Date": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox,
  },
  "extra__Planned Finish Date": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox,
  },
  "extra__RBD Approval Date": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox,
  },
  "extra__Scheduled Completion Date": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox,
  },
  "extra__Severity": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox,
  },
  "extra__Source of Finding": {
    "ui:widget": CustomDisabledTextBox,
    "ui:readonly": true
  },
  "extra__User Identfied Criticality": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox,
  },
  "extra__Weakness": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox,
  },
  "extra__Workflow Status": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox,
  },
  "extra__Workflow Status Date": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox,
  },
  "extra__Days Until Auto-Approved": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox,
  },
  "extra__Control Risk Severity": {
    "ui:readonly": true,
    "ui:widget": CustomDisabledTextBox,
  },



  "statement__status": {
    "ui:widget": CustomDisabledTextBox,
  },
  "statement__body": {
    "ui:widget": CustomDisabledTextBox,
  },
  "statement__import_record": {
    "ui:widget": CustomDisabledTextBox,
  },
  "statement__updated": {
    "ui:widget": CustomDisabledTextBox,
  },
  "statement__uuid": {
    "ui:widget": CustomDisabledTextBox,
  },
  "statement__remarks": {
    "ui:widget": CustomDisabledTextBox,
  },
  "statement__pid": {
    "ui:widget": CustomDisabledTextBox,
  },
  "statement__sid": {
    "ui:widget": CustomDisabledTextBox,
  },
  "statement__sid_class": {
    "ui:widget": CustomDisabledTextBox,
  },
  "statement__source": {
    "ui:widget": CustomDisabledTextBox,
  },
  "statement__created": {
    "ui:widget": CustomDisabledTextBox,
  }
}

export const SystemSummary = ({ systemId, projectId }) => {
  const dispatch = useDispatch();

  const classes = useStyles();
  const dgClasses = datagridStyles();
  const [data, setData] = useState([]);
  const [sortby, setSortBy] = useState(["name", "asc"]);
  const [ rows, setRows ] = useState(data);
  const [ searchText, setSearchText ] = useState('');
  const [columns, setColumns] = useState([]);

  const [openEditPoamModal, setOpenEditPoamModal] = useState(false);
  const [currentPoam, setCurrentPoam] = useState({})
  
  const elementRef = useRef(null);
  
  const handleClose = () => {
    setOpenEditPoamModal(false);
  }
  
  const handleOpenIndividualPoam = (row) => {
    setOpenEditPoamModal(true);
    const newpoam = flattenObject(row, 'data', 1);
    setCurrentPoam(newpoam);
    
    // Add Delay to wait for modal to finish, then grab reference and click to fix dropdown flutter caused 
    // by focus being taken away by a different element
    setTimeout(function() {
      elementRef.current.click();
    }, 500);
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
    axios(`/api/v2/systems/${systemId}/getSystemPoams/`).then(response => {
      setData(response.data.data);

      const newColumns = [
        {
            field: 'weakness_name',
            headerName: 'POA&M',
            width: 300,
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
      // debugger;
      if(response.data.data.length !== 0){
        for (const [key, value] of Object.entries(response.data.data[0].extra)) {
          if (key === "User Identified Criticality"){
            newColumns.push({
              field: key,
              headerName: key,
              width: 150,
              editable: ["Delay Justification", "Status as of June", "Comments"].includes(key) ? true : false,
              cellClassName: (params) =>
                clsx('super-app', {
                  critical: params.row.extra[key] === 'Critical',
                  advice: params.row.extra[key] === 'Advisory/Awareness',
                  target: params.row.extra[key] === 'On-Target',
                  closure: params.row.extra[key] === 'Closure Approved',
                  followup: params.row.extra[key] === 'Follow-up Required',
                  new: params.row.extra[key] === 'Newly Opened POAM'
                }
              ),
              valueGetter: (params) => params.row.extra[key] !== null ? params.row.extra[key] : "-"
            });
          } else {
            newColumns.push({
              field: key,
              headerName: key,
              width: 150,
              editable: ["Delay Justification", "Status as of June", "Comments"].includes(key) ? true : false,
              valueGetter: (params) => params.row.extra[key] !== null ? params.row.extra[key] : "-"
            });
          }
          
        }
      }
      
      const prioritySet = {
        'POA&M': 1,
        'Evidence': 2,
        'Status': 3,
        'Monthly Status': 4,
        'Severity': 5,
        'User Identified Criticality': 6,
        'CSFCategory': 7,
        'Delay Justification': 8,
        'Comments': 9,
        'Reported By': 10,
        'Date Reported': 11,
        'Cost': 12,
        'Email': 13,
        'Phone': 14,
        'Weakness': 15,
        'Assigned To': 16,
        'CSFFunction': 17,
        'Delay Reason': 18,
        'Accepted Risk': 19,
        'Assigned Date': 20,
        'POAM Sequence': 21,
        'CSFSubCategory': 22,
        'Criticality': 23,
        'Workflow Status': 24,
        'Number Artifacts': 25,
        'Actual Start Date': 26,
        'Number Milestones': 27,
        'RBD Approval Date': 28,
        'Source of Finding': 29,
        'Actual Finish Date': 30,
        'Planned Start Date': 31,
        'Days Since Creation': 32,
        'Deficiency Category': 33,        
        'Planned Finish Date': 34,
        'Workflow Status Date': 35,
        'Scheduled Completion Date': 36,
        'Control Risk Severity': 37,
        'Days Until Auto-Approved': 38
      }
      const sortedColumns = sortColumns(prioritySet, newColumns);
      
      setColumns(sortedColumns)
    });
  }, []);

  const sortColumns = (prioritySet, listOfColumns) => {
    // Add every column to a new array as a (column, priority#), sort by priority
    return listOfColumns.sort((a,b) => (prioritySet[a.headerName] > prioritySet[b.headerName]) ? 1 : -1)
  };

  const reconstruct = (formData, listOfSubObjNames) => {
    let data = {};

    for (let index in listOfSubObjNames) {
      const objName = listOfSubObjNames[index];
      data[objName] = {}

      Object.getOwnPropertyNames(formData).filter((att) => {
        if(att.includes('__')){
          if(att.includes(objName + '__')){
            data[objName][att.split(objName+'__')[1]] = formData[att]
            return att.split(objName+'__')[1];
          }
        } else {
          data[att] = formData[att]
        }
      });
    }
    
    return data
  }
  const onSubmit = async ( { formData }, e ) => {
    // PUT update to POAM to DB
    formData = reconstruct(formData, ['extra', 'statement'])

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
      setData(updatedRows);
      setRows(updatedRows);
      handleClose();
    } else {
      console.error("Something went wrong in creating and appointing new appointments")
    }
  };
  const flattenObject = (obj, title, level) => {
    const flattened = {}
    
    Object.keys(obj).forEach((key) => {
      const value = obj[key]
      
      if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
        Object.assign(flattened, flattenObject(value, key, level + 1))
      } else {
        if (level > 1){
          flattened[`${title}__${key}`] = value
        } else {
          flattened[key] = value
        }
      }
    })
    return flattened
  }

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
                          columns: {
                            columnVisibilityModel: {
                              // Hide columns status and traderName, the other columns will remain visible
                              severity: true,
                              "CSFCategory": true,
                              status: true,
                              "Monthly Status": true,
                              "Delay Justification": true,
                              "Comments": true,
                              "User Identified Criticality": true,

                              "risk_rating_adjusted": false,
                              "Cost": false,
                              "Email": false,
                              "Phone": false,
                              evidence: false,
                              created: false,
                              updated: false,
                              "Assigned To": false,
                              "Workflow Status Date": false,
                              "Scheduled Completion Date": false,
                              "Planned Start Date": false,
                              "Planned Finish Date": false,
                              "Actual Finish Date": false,
                              "Deficiency Category": false,
                              "Days Since Creation": false,
                              "Source of Finding": false,
                              "RBD Approval Date": false,
                              "Actual Start Date": false,
                              "Number Milestones": false,
                              "Number Artifacts": false,
                              "Workflow Status": false,
                              "CSFSubCategory": false,
                              "CSFFunction": false,
                              "Delay Reason": false,
                              "Accepted Risk": false,
                              "Assigned Date": false,
                              "POAM Sequence": false,
                              "Weakness": false,
                              'Control Risk Severity': false,
                              'Days Until Auto-Approved': false,
                              'Date % Complete Last Updated': false,
                              'Percent Complete': false,
                              'Exclude From OMB': false,
                            }
                          },
                        }}

                        // components={{ Toolbar: CustomToolbar }}
                        
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
          <ReactModal
            title={`Edit POAM`}
            dialogClassName={"poam-edit-modal"}
            show={openEditPoamModal}
            hide={() => setOpenEditPoamModal(false)}
            header={
              <span>Update POAM {currentPoam.id}: {currentPoam.weakness_name}</span>
            }
            body={
              <div style={{width: '100% !important', height: '100% !important', margin: '2rem'}}>
                <div className='row' id="form-div" ref={elementRef}> 
                    <Form
                      formData={currentPoam}
                      schema={schema}
                      uiSchema={uiSchema}
                      fields={fields}
                      // widgets={widgets}
                      onSubmit={onSubmit}
                      noHtml5Validate={true}
                    />
                  {/* </div> */}
                </div>
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
  )
}