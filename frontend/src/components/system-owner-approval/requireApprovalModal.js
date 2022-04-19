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

export const RequireApprovalModal = ({ systemId, isOwner }) => {
  const dispatch = useDispatch();

  const classes = useStyles();
  const dgClasses = datagridStyles();
  const [data, setData] = useState([]);
  const [openRequireApprovalModal, setOpenRequireApprovalModal] = useState(false);
  
  const endpoint = (querystrings) => {
    return axios.get(`/api/v2/roles/`, { params: querystrings });
  };


  useEffect(() => {
      axios(`/api/v2/elements/${elementId}/`).then(response => {
        setData(response.data.parties);
      });
  }, [])

  const handleSubmit = async (event) => {
    console.log('handleSubmit!')
  }

  return (
    <div style={{ maxHeight: '2000px', width: '100%' }}>
      <ReactModal
          title={`Create New Party with appointed roles`}
          show={openRequireApprovalModal}
          hide={() => setOpenRequireApprovalModal(false)}
          header={
            <Form horizontal>
              <>
                <FormGroup controlId={`form-title`}>
                  <Col sm={12}>
                    <h3>You have selected a "protected" common control component.</h3>
                  </Col>
                </FormGroup>
              </>
            </Form>
          }
          body={
            <Form horizontal onSubmit={handleSubmit}>
              <FormGroup>
                <div 
                  style={{ 
                    marginLeft: '6rem', 
                    marginBottom: '2rem', 
                    width: '80%', 
                  }}
                >
                    <p>The {element.full_name} common control set required approval/whitelist.</p>
                    
                </div>
              </FormGroup>
              <Modal.Footer style={{width: 'calc(100% + 20px)'}}>
                  <Button type="button" onClick={clearModal} style={{float: 'left'}}>Clear</Button>
                  <Button variant="secondary" onClick={handleClose} style={{marginRight: '2rem'}}>Close</Button>
                  <Button type="submit" bsStyle="success">Save Changes</Button>
              </Modal.Footer>
              </Form>
          }
        />
    </div>
  )
}