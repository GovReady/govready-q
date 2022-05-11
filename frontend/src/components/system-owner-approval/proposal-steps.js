import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { 
    Button,
    Grid,
} from '@mui/material';
import { makeStyles } from '@mui/styles';
import { ListGroup, ListGroupItem } from 'react-bootstrap';

const useStyles = makeStyles({
    root: {
      fontweight: 900,
    },
    completed: {
        backgroundColor: '#dae0d2',
        '& .dot': {
            marginLeft: '1rem',
            marginTop: '1rem',
            width: '75px', 
            height: '75px', 
            backgroundColor: '#06b30d', 
            borderRadius: '50%', 
            display: 'inline-block'
        }
    },
    current: {
        backgroundColor: '#ffffe3',
        '& .dot': {
            marginLeft: '1rem',
            marginTop: '1rem',
            width: '75px', 
            height: '75px', 
            backgroundColor: '#ffb404',
            borderRadius: '50%', 
            display: 'inline-block'
        }
    },
    notStarted: {
        backgroundColor: 'white',
        '& .dot': {
            marginLeft: '1rem',
            marginTop: '1rem',
            width: '75px', 
            height: '75px', 
            backgroundColor: '#717171', 
            borderRadius: '50%', 
            display: 'inline-block'
        }
    },
});

export const ProposalSteps = ({ userId, system, element, proposal, request, hasSentRequest }) => {
    const classes = useStyles(proposal.status);

    useEffect(() => {
        if(hasSentRequest && request){
            
            if(proposal.status.toLowerCase() !== 'approval' && request.status.toLowerCase() === 'approve'){
                const updatedProposal = {
                    "user": userId,
                    "requested_element": parseInt(element.id),
                    "criteria_comment": proposal.criteria_comment,
                    "status": "Approval",
                }
                const updateProposalApproval = axios.put(`/api/v2/proposals/${parseInt(proposal.id)}/`, updatedProposal);
                if(updateProposalApproval.status === 200){
                    addComponentStatements();
                    // window.location.reload();
                } else {
                    console.error("Something went wrong in updating proposal1");
                }
            } else if(proposal.status.toLowerCase() === 'approval' && request.status.toLowerCase() !== 'approve'){
                const updatedProposalToRequest = {
                    "user": userId,
                    "requested_element": parseInt(element.id),
                    "criteria_comment": proposal.criteria_comment,
                    "status": "Request",
                }
                const updateProposalToNewStatus = axios.put(`/api/v2/proposals/${parseInt(proposal.id)}/`, updatedProposalToRequest);
                if(updateProposalToNewStatus.status === 200){
                    window.location.reload();
                } else {
                    console.error("Something went wrong in updating proposal2");
                }
            } else {
                console.log('everything else');
            }
        }
    }, []);
    
    const getStatusLevel = (status) => {
        switch (status.toLowerCase()) {
            case 'planning':
                return 1;
            case 'request':
                return 2;
            case 'approval':
                return 3;
            case 'additionalSteps':
                return 4;
            case 'closed':
                return 5;
            default:
                return 0;
        }
    }

    const successful_request_message = (systemName, elementName) => {
        const message = `System ${systemName} has proposed ${elementName}`;
        document.getElementById("req_message_type").value = "INFO";
        document.getElementById("req_message").value = message;
        document.send_request_message.submit()
      }
    
      const send_alreadyRequest_message = (systemName, elementName) => {
        const message = `System ${systemName} has already proposed ${elementName}.`;
        document.getElementById("req_message_type").value = "WARNING";
        document.getElementById("req_message").value = message;
        document.send_request_message.submit()
      }

    const submitRequest = async () => {
        const newReq = {
          userId: userId,
          systemId: system.id,
          criteria_comment: proposal.criteria_comment,
          criteria_reject_comment: "",
          status: "open",
        }

        const checkElement = await axios.get(`/api/v2/elements/${element.id}/retrieveRequests/`);
        if(checkElement.status === 200){
          let alreadyRequested = false;
          checkElement.data.requested.map((req) => {
            if((req.userId === userId) && (req.requested_element.id === parseInt(element.id)) && (req.system.id === newReq.systemId)){
              alreadyRequested = true;
            }
          });
          if(!alreadyRequested){
            /* Create a request and assign it to element and system */
            const newRequestResponse = await axios.post(`/api/v2/elements/${element.id}/CreateAndSetRequest/`, newReq);
            if(newRequestResponse.status === 200){
                successful_request_message(system.name, element.name);
            } else {
              console.error("Something went wrong in creating and setting new request to element");
            }
          } else {
            send_alreadyRequest_message(system.name, element.name);
          }
        } else {
          console.error("Something went wrong with checking element");
        }
    }

    const completePlanningPhase = async () => {
        const updatedProposal = {
            "user": userId,
            "requested_element": element.id,
            "criteria_common": proposal.criteria_common,
            "status": "Request",
        }

        const updateProposalCall = await axios.put(`/api/v2/proposals/${proposal.id}/`, updatedProposal);
        if(updateProposalCall.status === 200){
            window.location.reload();
        } else {
            console.error("Something went wrong in updating proposal");
        }
    }

    const addComponentStatements = async () => {
        ajax_with_indicator({
            url: `/systems/${parseInt(system.id)}/components/add_system_component`,
            method: "POST",
            data: {
                producer_element_id: `${parseInt(element.id)},False`,
                redirect_url: `/systems/${parseInt(system.id)}/components/selected`,
            },
            // system_id: system.id,
            success: function(res) {
                ajax_with_indicator({
                    url: `/systems/${parseInt(system.id)}/components/remove_proposal/${parseInt(proposal.id)}`,
                    method: "POST",
                    data: {
                        system_id: system.id,
                        proposal_id: proposal.id,
                        element_id: element.id,
                    },
                    // system_id: system.id,
                    success: function(res) {
                        // redirect to main project page after successful upgrade
                        window.location = `/systems/${parseInt(system.id)}/components/selected`
                    }
                });
                
            }
        });
    }

    return (
        <div>
            {element.require_approval && <ListGroup>
                <ListGroupItem className={getStatusLevel(proposal.status) === 1 ? classes.current : getStatusLevel(proposal.status) > 1 ? classes.completed : classes.notStarted}>
                    <Grid container>
                        <Grid item xs={3}>
                            <span className="dot"></span>
                        </Grid>
                        <Grid item xs={9}>
                            <div><h2>Planning</h2></div>
                            <div><h4>List of criteria:</h4></div>
                            <div>
                                <div style={{ whiteSpace: 'break-spaces' }}>
                                    {proposal.criteria_comment === '' ? "Criteria has not been set" : proposal.criteria_comment}
                                </div>
                                <div style={{float: 'right'}}>
                                    {getStatusLevel(proposal.status) === 1 && <Button variant="contained" onClick={completePlanningPhase}>Completed Planning</Button>}
                                </div>
                            </div>
                        </Grid>
                    </Grid>
                </ListGroupItem>
                <ListGroupItem className={getStatusLevel(proposal.status) === 2 ? classes.current : getStatusLevel(proposal.status) > 2 ? classes.completed : classes.notStarted}>
                    <Grid container>
                        <Grid item xs={3}>
                            <span className="dot"></span>
                        </Grid>
                        <Grid item xs={9}>
                            <div><h2>Request</h2></div>
                            {hasSentRequest ? <div>You have already requested access to the {element.name} and its related controls.</div> : <div>Please submit a request.</div>}
                            <div style={{float: 'right'}}>
                                {getStatusLevel(proposal.status) === 2 && hasSentRequest !== true && <Button variant="contained" onClick={submitRequest}>Submit Request</Button>}
                            </div>
                            {hasSentRequest ? <div>Status of request: <b>{request.status}</b></div> : null}
                        </Grid>
                    </Grid>
                </ListGroupItem>
                <ListGroupItem className={getStatusLevel(proposal.status) === 3 ? classes.completed : getStatusLevel(proposal.status) > 3 ? classes.completed : classes.notStarted}>
                    <Grid container>
                        <Grid item xs={3}>
                            <span className="dot"></span>
                        </Grid>
                        <Grid item xs={9}>
                            <div><h2>Approval</h2></div>
                            <div>The confirmation fo system using {element.name} from component owner. System can proceed to use the component.</div>
                            <div style={{float: 'right'}}>
                            {getStatusLevel(proposal.status) === 3 && hasSentRequest === true &&<Button variant="contained" onClick={addComponentStatements}>Add Selected Componenet</Button>}
                            </div>
                        </Grid>
                    </Grid>
                </ListGroupItem>
                <ListGroupItem className={getStatusLevel(proposal.status) === 3 ? classes.current : getStatusLevel(proposal.status) > 3 ? classes.completed : classes.notStarted}>
                    <Grid container>
                        <Grid item xs={3}>
                            <span className="dot"></span>
                        </Grid>
                        <Grid item xs={9}>
                            <div><h2>Additional Steps</h2></div>
                            <div>Technical team will need to understack various activities to configure your {element.name} (Paas-Server Service).</div>
                        </Grid>
                    </Grid>
                </ListGroupItem>
            </ListGroup>}
        </div>
    );
};