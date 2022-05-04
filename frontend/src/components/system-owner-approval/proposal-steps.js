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
            width: '75px', 
            height: '75px', 
            backgroundColor: '#717171', 
            borderRadius: '50%', 
            display: 'inline-block'
        }
    },
});

export const ProposalSteps = ({ userId, systemId, elementId, systemName, elementName, proposalStatus, proposalCriteria, hasSentRequest }) => {
    
    const [status, setStatus] = useState({
        open: proposalStatus.toLowerCase() === 'open' ? true : false,
        planning: proposalStatus.toLowerCase() === 'planning' ? true : false,
        request: proposalStatus.toLowerCase() === 'request' ? true : false,
        approval: proposalStatus.toLowerCase() === 'approval' ? true : false,
        additionalSteps: proposalStatus.toLowerCase() === 'additionalSteps' ? true : false,
    });
    const classes = useStyles(status);

    useEffect(() => {
        switch(proposalStatus) {
            case 'open':
                setStatus((prev) => ({
                    ...prev,
                    open: true,
                }));
                break;
            case 'planning':
                setStatus((prev) => ({
                    ...prev,
                    planning: true,
                }));
                break;
            case 'request':
                setStatus((prev) => ({
                    ...prev,
                    request: true,
                }));
                break;
            case 'approval':
                setStatus((prev) => ({
                    ...prev,
                    approval: true,
                }));
                break;
            case 'additionalSteps':
                setStatus((prev) => ({
                    ...prev,
                    additionalSteps: true,
                }));
                break;
            default:
                setStatus((prev) => ({
                    ...prev,
                    planning: false,
                    request: false,
                    approval: false,
                    additionalSteps: false,
                }));
        }
    }, [proposalStatus]);
    const getStatusLevel = (status) => {
        console.log('status: ', status)
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
    const successful_proposal_message = (systemName, elementName) => {
        const message = `System ${systemName} has proposed ${elementName}`;
        document.getElementById("req_message_type").value = "INFO";
        document.getElementById("req_message").value = message;
        document.send_request_message.submit()
      }
    
      const send_alreadyProposed_message = (systemName, elementName) => {
        const message = `System ${systemName} has already proposed ${elementName}.`;
        document.getElementById("req_message_type").value = "WARNING";
        document.getElementById("req_message").value = message;
        document.send_request_message.submit()
      }

    const submitRequest = async () => {
        console.log('submitRequest!');
        const newReq = {
          userId: userId,
          systemId: systemId,
          criteria_comment: proposalCriteria,
          criteria_reject_comment: "",
          status: "open",
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
              successful_proposal_message(systemName, elementName);
            } else {
              console.error("Something went wrong in creating and setting new request to element");
            }
          } else {
            send_alreadyProposed_message(systemName, elementName);
          }
        } else {
          console.error("Something went wrong with checking element");
        }
    }

    return (
        <div>
            <ListGroup>
                <ListGroupItem className={getStatusLevel(proposalStatus) === 1 ? classes.current : getStatusLevel(proposalStatus) > 1 ? classes.completed : classes.notStarted}>
                    <Grid container >
                        <Grid item xs={3}>
                            <span className="dot"></span>
                        </Grid>
                        <Grid item xs={9}>
                            <div><h2>Open</h2></div>
                            <div><h4>Proposal has been opened.</h4></div>
                            <div>{proposalCriteria === '' ? "Criteria has not been set" : proposalCriteria}</div>
                        </Grid>
                    </Grid>
                </ListGroupItem>
                <ListGroupItem className={getStatusLevel(proposalStatus) === 2 ? classes.current : getStatusLevel(proposalStatus) > 2 ? classes.completed : classes.notStarted}>
                    <Grid container>
                        <Grid item xs={3}>
                            <span className="dot"></span>
                        </Grid>
                        <Grid item xs={9}>
                            <div><h2>Planning</h2></div>
                            <div><h4>List</h4></div>
                            <div>{proposalCriteria === '' ? "Criteria has not been set" : proposalCriteria}</div>
                        </Grid>
                    </Grid>
                </ListGroupItem>
                <ListGroupItem className={getStatusLevel(proposalStatus) === 3 ? classes.current : getStatusLevel(proposalStatus) > 3 ? classes.completed : classes.notStarted}>
                    <Grid container>
                        <Grid item xs={3}>
                            <span className="dot"></span>
                        </Grid>
                        <Grid item xs={9}>
                            <div><h2>Request</h2></div>
                            <div>You have requested access to the {elementName} and its related controls.</div>
                            <div style={{float: 'right'}}>
                                {/* 
                                    Request button will only appear if
                                        1. user is not the owner of the element
                                        2. request has not been previously made
                                        3. proposal is not currently at the request status stage
                                */}
                                {getStatusLevel(proposalStatus) === 3 && hasSentRequest !== true && <Button variant="contained" onClick={submitRequest}>Submit Request</Button>}
                            </div>
                        </Grid>
                    </Grid>
                </ListGroupItem>
                <ListGroupItem className={getStatusLevel(proposalStatus) === 4 ? classes.current : getStatusLevel(proposalStatus) > 4 ? classes.completed : classes.notStarted}>
                    <Grid container>
                        <Grid item xs={3}>
                            <span className="dot"></span>
                        </Grid>
                        <Grid item xs={9}>
                            <div><h2>Approval</h2></div>
                            <div>The confirmation fo system using {elementName} from component owner. System can proceed to use the component.</div>
                        </Grid>
                    </Grid>
                </ListGroupItem>
                <ListGroupItem className={getStatusLevel(proposalStatus) === 5 ? classes.current : getStatusLevel(proposalStatus) > 5 ? classes.completed : classes.notStarted}>
                    <Grid container>
                        <Grid item xs={3}>
                            <span className="dot"></span>
                        </Grid>
                        <Grid item xs={9}>
                            <div><h2>Additional Steps</h2></div>
                            <div>Technical team will need to understack various activities to configure your {elementName} (Paas-Server Service).</div>
                        </Grid>
                    </Grid>
                </ListGroupItem>
            </ListGroup>
        </div>
    );
};