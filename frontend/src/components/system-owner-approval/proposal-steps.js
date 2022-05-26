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
        backgroundColor: '#ffffff',
        '& .dot': {
            marginLeft: '1rem',
            marginTop: '1rem',
            width: '50px',
            height: '50px',
            backgroundColor: '#06b30d',
            borderRadius: '50%',
            display: 'inline-block'
          },
        '& .glyphicon-ok': {
              color:'#ffffff',
              fontSize:'24px',
              padding:'12px 0 0 13px'
        },
      '& .glyphicon-remove': {
            display: 'none !important',
            position: 'absolute !important',
            top: '-9999px !important',
            left: '-9999px !important'
      },
      '& .glyphicon-paperclip': {
            display: 'none !important',
            position: 'absolute !important',
            top: '-9999px !important',
            left: '-9999px !important'
      }
    },
    current: {
        backgroundColor: '#ffffe3',
        '& .dot': {
            marginLeft: '1rem',
            marginTop: '1rem',
            width: '50px',
            height: '50px',
            backgroundColor: '#ffb404',
            borderRadius: '50%',
            display: 'inline-block'
        },
      '& .glyphicon-ok': {
            display: 'none !important',
            position: 'absolute !important',
            top: '-9999px !important',
            left: '-9999px !important'
      },
      '& .glyphicon-paperclip': {
            color:'#ffffff',
            fontSize:'24px',
            padding:'12px 0 0 14px'
      },
    '& .glyphicon-plus': {
      color:'#ffffff',
      fontSize:'24px',
      padding:'12px 0 0 14px'
    },
  '& .glyphicon-remove': {
        display: 'none !important',
        position: 'absolute !important',
        top: '-9999px !important',
        left: '-9999px !important'
  }
    },
    currentRejected: {
        backgroundColor: '#ffffe3',
        '& .dot': {
            marginLeft: '1rem',
            marginTop: '1rem',
            width: '50px',
            height: '50px',
            backgroundColor: 'red',
            borderRadius: '50%',
            display: 'inline-block'
        },
      '& .glyphicon-remove': {
            color:'#ffffff',
            fontSize:'24px',
            padding:'13px 0 0 13px'
      }
    },
    notStarted: {
        backgroundColor: 'white',
        color: '#B3B3B3',
        '& .dot': {
            marginLeft: '1rem',
            marginTop: '1rem',
            width: '50px',
            height: '50px',
            backgroundColor: '#B3B3B3',
            borderRadius: '50%',
            display: 'inline-block'
        },
      '& .glyphicon-ok': {
            display: 'none !important',
            position: 'absolute !important',
            top: '-9999px !important',
            left: '-9999px !important'
      },
      '& .glyphicon-plus': {
        display: 'none !important',
        position: 'absolute !important',
        top: '-9999px !important',
        left: '-9999px !important'
      },
      '& .glyphicon-paperclip': {
            display: 'none !important',
            position: 'absolute !important',
            top: '-9999px !important',
            left: '-9999px !important'
      },
    '& .glyphicon-remove': {
          display: 'none !important',
          position: 'absolute !important',
          top: '-9999px !important',
          left: '-9999px !important'
    }
    },
});

export const ProposalSteps = ({ userId, system, element, proposal, request, hasSentRequest }) => {
    const classes = useStyles(proposal.status);

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
            proposalId: proposal.id,
            userId: userId,
            systemId: system.id,
            criteria_comment: proposal.criteria_comment,
            criteria_reject_comment: "",
            status: "Open",
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
            success: function(res) {
                ajax_with_indicator({
                    url: `/systems/${parseInt(system.id)}/components/remove_proposal/${parseInt(proposal.id)}`,
                    method: "POST",
                    data: {
                        system_id: system.id,
                        proposal_id: proposal.id,
                        element_id: element.id,
                    },
                    success: function(res) {
                        // redirect to main project page after successful upgrade
                        window.location = `/systems/${parseInt(system.id)}/components/selected`
                    }
                });

            }
        });
    }

    const getCurrentStatusLevel = () => {
        if(proposal.status.toLowerCase() === 'request'){
            if (hasSentRequest && request.status.toLowerCase() === 'approve') {
                return classes.completed
            } else if (hasSentRequest && request.status.toLowerCase() === 'reject') {
                return classes.currentRejected
            } else {
                return classes.current
            }
        } else {
            return classes.notStarted
        }
    }

    return (
        <div>
            {element.require_approval && proposal.id !== '' && <ListGroup>
                <ListGroupItem className={getStatusLevel(proposal.status) === 1 ? classes.current : getStatusLevel(proposal.status) > 1 ? classes.completed : classes.notStarted}>
                    <Grid container>
                        <Grid item xs={1}>
                            <span className="dot"><span className="glyphicon glyphicon-ok"></span><span className="glyphicon glyphicon-paperclip"></span></span>

                        </Grid>
                        <Grid item xs={9}>
                            <div className="step-box"><h4>Planning</h4>
                            <p className="step-box-content">List of criteria:
                                <div style={{ whiteSpace: 'break-spaces' }}>
                                    {proposal.criteria_comment === '' ? "Criteria has not been set" : proposal.criteria_comment}
                                </div></p>

                            </div>
                        </Grid>
                        <Grid item xs={2}><div style={{float: 'right'}}>
                            {getStatusLevel(proposal.status) === 1 && <Button variant="contained" onClick={completePlanningPhase}>Completed Planning</Button>}
                        </div>
                        </Grid>
                    </Grid>
                </ListGroupItem>
                <ListGroupItem className={getCurrentStatusLevel()}>
                    <Grid container>
                        <Grid item xs={1}>
                            <span className="dot"><span className="glyphicon glyphicon-ok"></span><span className="glyphicon glyphicon-paperclip"></span><span className="glyphicon glyphicon-remove"></span></span>
                        </Grid>
                        <Grid item xs={9}>
                            <div className="step-box"><h4>Request</h4>
                            {hasSentRequest ? <div><p className="step-box-content">You have requested access to the {element.name} and its related controls. Status: <strong>{request.status}</strong></p></div> : <div><p className="step-box-content">Please submit a request.</p></div>}


                            </div>
                        </Grid>
                        <Grid item xs={2}><div style={{float: 'right'}}>
                            {getStatusLevel(proposal.status) === 2 && hasSentRequest !== true && <Button variant="contained" onClick={submitRequest}>Submit Request</Button>}
                        </div></Grid>
                    </Grid>
                </ListGroupItem>
                <ListGroupItem className={request.status.toLowerCase() === "approve" ? classes.completed : getStatusLevel(proposal.status) > 3 ? classes.completed : classes.notStarted}>
                    <Grid container>
                        <Grid item xs={1}>
                            <span className="dot"><span className="glyphicon glyphicon-ok"></span></span>
                        </Grid>
                        <Grid item xs={9}>
                            <div className="step-box"><h4>Approval</h4>
                            <p className="step-box-content">The confirmation of system using {element.name} from component owner. System can proceed to use the component.</p>
                            </div>
                        </Grid>
                          <Grid item xs={2}><div style={{float: 'right'}}>{getStatusLevel(proposal.status) === 3 && hasSentRequest === true &&<Button variant="contained" onClick={addComponentStatements}>Add Selected Component</Button>}</div>
                          </Grid>
                    </Grid>
                </ListGroupItem>
                <ListGroupItem className={request.status.toLowerCase() === "approve" ? classes.current : getStatusLevel(proposal.status) > 3 ? classes.completed : classes.notStarted}>
                    <Grid container>
                        <Grid item xs={1}>
                            <span className="dot"><span className="glyphicon glyphicon-plus"></span></span>
                        </Grid>
                        <Grid item xs={11}>
                            <div className="step-box"><h4>Additional Steps</h4>
                            <p className="step-box-content">Technical team will need to understack various activities to configure your {element.name} (Paas-Server Service).</p>
                            </div>
                        </Grid>
                    </Grid>
                </ListGroupItem>
            </ListGroup>}
        </div>
    );
};
