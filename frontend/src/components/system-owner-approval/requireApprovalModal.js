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
import { element } from 'prop-types';

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

export const RequireApprovalModal = ({ userId, systemId, elementId, require_approval, uuid }) => {
  const classes = useStyles();
  const dgClasses = datagridStyles();
  const [data, setData] = useState([]);
  const [openRequireApprovalModal, setOpenRequireApprovalModal] = useState(false);

  useEffect(() => {
    axios(`/api/v2/elements/${elementId}/`).then(response => {
      setData(response.data);
      if(require_approval || response.data.criteria.length > 0){
        setOpenRequireApprovalModal(true);
      }
      if(!require_approval && response.data.criteria === ""){
        /* add_component form can be found in systems/component_selected.html */
        document.add_component.submit(); 
      }
    });
  }, [elementId, uuid])

  const handleAddComponent = () => {
    handleClose();
    document.add_component.submit();
  }

  const handleSubmit = async (event) => {
    event.preventDefault();
    
    const newReq = {
      userId: userId,
      systemId: systemId,
      criteria_comment: data.criteria,
      criteria_reject_comment: "",
      status: "pending"
    }
    const checkElement = await axios.get(`/api/v2/elements/${elementId}/retrieveRequests/`);

    if(checkElement.status === 200){
      let alreadyRequested = false;
      checkElement.data.requested.map((req) => {
        if((req.userId === userId) && (req.requested_element.id === parseInt(elementId)) && (req.system.id === newReq.systemId)){
          alreadyRequested = true;
        }
      });
      if(!alreadyRequested){
        /* Create a request and assign it to element and system */
        const newRequestResponse = await axios.post(`/api/v2/elements/${elementId}/CreateAndSetRequest/`, newReq);
        if(newRequestResponse.status === 200){
          handleClose();
        } else {
          console.error("Something went wrong in creating and setting new request to element");
        }
      } else {
        handleClose();
        alert('ALREADY REQUESTED!');
      }
    } else {
      console.error("Something went wrong with checking element");
    }
  }
  const handleClose = async (event) => {
    setOpenRequireApprovalModal(false);
  }
  
  return (
    <div style={{ maxHeight: '2000px', width: '100%' }}>
      {data !== null && <ReactModal
        title={`System Owner Requesting Element Modal`}
        show={openRequireApprovalModal}
        hide={() => setOpenRequireApprovalModal(false)}
        dialogClassName={"sys-owner-request-modal"}
        header={
          <Form horizontal style={{ paddingLeft: '4rem', paddingRight: '4rem' }}>
            <h2>You have selected {require_approval ? <span>a "protected"</span> : <span>a</span>} common control component.</h2>
          </Form>
        }
        headerStyle={{
          backgroundColor: '#FFFFF7',
          border: 'none',
        }}
        body={
          <Form horizontal onSubmit={handleSubmit}>
              <div 
                style={{ 
                  marginLeft: '6rem', 
                  marginBottom: '2rem', 
                  width: '80%', 
                }}
              >
                {require_approval ? <p>The {data.full_name} common control has set an approval/whitelist requirement.</p> : <p>The {data.full_name} common control has not set required approval/whitelist, but has criteria that must be met.</p>}
                {data.criteria ? <span style={{ whiteSpace: 'break-spaces' }}>{data.criteria}</span> : <span>No criteria has been set</span>}
              </div>
            <Modal.Footer style={{ border: 'none' }}>
                <Button type="button" onClick={handleClose} style={{float: 'left'}}>Cancel</Button>
                {
                  !require_approval && data.criteria ? 
                  <Button type="button" bsStyle="success" onClick={handleAddComponent} style={{float: 'right'}}>Add Component</Button> :
                  <Button type="submit" bsStyle="success">Submit Request</Button> 
                }
            </Modal.Footer>
          </Form>
        }
        bodyStyle={{
          backgroundColor: '#FFFFF7',
          border: 'none',
        }}
      />
    }
    </div>
  )
}