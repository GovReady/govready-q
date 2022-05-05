import React, { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { DataTable } from '../shared/table';
import axios from 'axios';
import moment from 'moment';
import { DataGrid } from '@mui/x-data-grid';
import { v4 as uuid_v4 } from "uuid";
import { 
    Button,
    Chip,
    Grid,
    Stack,
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

export const ProposalSteps = ({ userId, system, element, proposal, hasSentRequest }) => {
    
    // const [status, setStatus] = useState({
    //     open: proposalStatus.toLowerCase() === 'open' ? true : false,
    //     planning: proposalStatus.toLowerCase() === 'planning' ? true : false,
    //     request: proposalStatus.toLowerCase() === 'request' ? true : false,
    //     approval: proposalStatus.toLowerCase() === 'approval' ? true : false,
    //     additionalSteps: proposalStatus.toLowerCase() === 'additionalSteps' ? true : false,
    // });
    const classes = useStyles(proposal.status);

    // useEffect(() => {
    //     switch(proposalStatus) {
    //         case 'open':
    //             setStatus((prev) => ({
    //                 ...prev,
    //                 open: true,
    //             }));
    //             break;
    //         case 'planning':
    //             setStatus((prev) => ({
    //                 ...prev,
    //                 planning: true,
    //             }));
    //             break;
    //         case 'request':
    //             setStatus((prev) => ({
    //                 ...prev,
    //                 request: true,
    //             }));
    //             break;
    //         case 'approval':
    //             setStatus((prev) => ({
    //                 ...prev,
    //                 approval: true,
    //             }));
    //             break;
    //         case 'additionalSteps':
    //             setStatus((prev) => ({
    //                 ...prev,
    //                 additionalSteps: true,
    //             }));
    //             break;
    //         default:
    //             setStatus((prev) => ({
    //                 ...prev,
    //                 planning: false,
    //                 request: false,
    //                 approval: false,
    //                 additionalSteps: false,
    //             }));
    //     }
    // }, [proposalStatus]);
    
    const getStatusLevel = (status) => {
        switch (status.toLowerCase()) {
            case 'open':
                return 1;
            case 'planning':
                return 2;
            case 'request':
                return 3;
            case 'approval':
                return 4;
            case 'additionalSteps':
                return 5;
            case 'closed':
                return 6;
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
        console.log('submitRequest!');
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
        console.log('completePlanning!');
        const updatedProposal = {
            "user": userId,
            "requested_element": element.id,
            "criteria_common": proposal.criteria_common,
            "status": "Request",
        }

        const updateProposalCall = await axios.put(`/api/v2/proposals/${proposal.id}/`, updatedProposal);
        if(updateProposalCall.status === 200){
            console.log("Proposal updated!");
        } else {
            console.error("Something went wrong in updating proposal");
        }
    }

    console.log('system: ', system);
    console.log('element: ', element);
    console.log('proposal: ', proposal);
    console.log('hasSentRequest: ', hasSentRequest);
    return (
        <div>
            <ListGroup>
                <ListGroupItem className={getStatusLevel(proposal.status) === 2 ? classes.current : getStatusLevel(proposal.status) > 2 ? classes.completed : classes.notStarted}>
                    <Grid container>
                        <Grid item xs={3}>
                            <span className="dot"></span>
                        </Grid>
                        <Grid item xs={9}>
                            <div><h2>Planning</h2></div>
                            <div><h4>List</h4></div>
                            <div>
                                <div>
                                    {proposal.criteria_comment === '' ? "Criteria has not been set" : proposal.criteria_comment}
                                </div>
                                <div>
                                    {getStatusLevel(proposal.status) === 3 && <Button variant="contained" onClick={completePlanning}>Completed Planning</Button>}
                                </div>
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
                            <div><h2>Request</h2></div>
                            <div>You have requested access to the {element.name} and its related controls.</div>
                            <div style={{float: 'right'}}>
                                
                                {getStatusLevel(proposal.status) === 3 && hasSentRequest !== true && <Button variant="contained" onClick={submitRequest}>Submit Request</Button>}
                            </div>
                        </Grid>
                    </Grid>
                </ListGroupItem>
                <ListGroupItem className={getStatusLevel(proposal.status) === 4 ? classes.current : getStatusLevel(proposal.status) > 4 ? classes.completed : classes.notStarted}>
                    <Grid container>
                        <Grid item xs={3}>
                            <span className="dot"></span>
                        </Grid>
                        <Grid item xs={9}>
                            <div><h2>Approval</h2></div>
                            <div>The confirmation fo system using {element.name} from component owner. System can proceed to use the component.</div>
                        </Grid>
                    </Grid>
                </ListGroupItem>
                <ListGroupItem className={getStatusLevel(proposal.status) === 5 ? classes.current : getStatusLevel(proposal.status) > 5 ? classes.completed : classes.notStarted}>
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
            </ListGroup>
        </div>
    );
};