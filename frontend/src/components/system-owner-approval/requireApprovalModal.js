import React, { useEffect, useState } from 'react';
import axios from 'axios';
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
import { ReactModal } from '../shared/modal';

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

export const RequireApprovalModal = ({ userId, systemId, systemName, elementId, require_approval, uuid }) => {
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

  const error_no_controls = () => {
    const message = `I couldn\'t add "${data.name}" to the system because the component does not currently have any control implementation statements to add.`
    document.getElementById("proposal_message_type").value = "ERROR";
    document.getElementById("proposal_message").value = message;
    document.send_proposal_message.submit()
  }
  const successful_proposal_message = () => {
    /* A template literal. It is a string that allows embedded expressions. */
    const message = `System ${systemName} has proposed ${data.name}`;
    document.getElementById("proposal_message_type").value = "INFO";
    document.getElementById("proposal_message").value = message;
    document.send_proposal_message.submit()
    // ajax_with_indicator({
    //     url: `/systems/${parseInt(systemId)}/components/proposal_message`,
    //     method: "POST",
    //     data: {
    //       proposal_message_type: "INFO",
    //       proposal_message: message,
    //     },
    //     // system_id: system.id,
    //     success: function(res) {
    //         console.log("successful_proposal_message SUCCESSFUL!!@!#!")
    //         window.location.reload();
    //     }
    // });
  }

  const send_alreadyProposed_message = () => {
    const message = `System ${systemName} has already proposed ${data.name}.`;
    document.getElementById("proposal_message_type").value = "WARNING";
    document.getElementById("proposal_message").value = message;
    document.send_proposal_message.submit()
  }

  const handleAddComponent = () => {
    handleClose();
    document.add_component.submit();
  }

  const handleSubmit = async (event) => {
    event.preventDefault();

    if(data.numOfStmts === 0){
      handleClose();
      error_no_controls();
    } else {
      const newProposal = {
        userId: userId,
        elementId: elementId,
        criteria_comment: data.criteria,
        status: "Planning"
      }

      const checkSystem = await axios.get(`/api/v2/systems/${systemId}/retrieveProposals/`);
      if(checkSystem.status === 200){
        let alreadyProposed = false;
        checkSystem.data.proposals.map((req) => {
          if(req.elementId === parseInt(elementId)){
            alreadyProposed = true;
          }
        });
        if(!alreadyProposed){
          /* Create a request and assign it to element and system */
          const newRequestResponse = await axios.post(`/api/v2/systems/${systemId}/CreateAndSetProposal/`, newProposal);
          if(newRequestResponse.status === 200){
            handleClose();
            successful_proposal_message();
          } else {
            console.error("Something went wrong in creating and setting new proposal to element");
          }
        } else {
          handleClose();
          send_alreadyProposed_message();
        }
      } else {
        console.error("Something went wrong with checking element");
      }
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
                  <Button type="submit" bsStyle="success">Create proposed component</Button> 
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