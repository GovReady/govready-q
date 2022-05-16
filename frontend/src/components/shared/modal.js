import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Modal } from 'react-bootstrap';

import { hide, show } from './modalSlice';

import "../../index.css";

export const ReactModal = (props) => {
    const dispatch = useDispatch();
    const modalStatus = useSelector(state => state.modal.value)
    
    return (
        <>
            <Modal
                show={props.show}
                onHide={props.hide}
                aria-labelledby="react-modal"
                dialogClassName={props.dialogClassName ? props.dialogClassName : "react-modal"}
            >
                <Modal.Header closeButton style={props.headerStyle ? props.headerStyle : { backgroundColor: "#e5e5e5", }}
                >
                    <Modal.Title id="modal-title">
                        {props.header}
                    </Modal.Title>
                </Modal.Header>
                <Modal.Body
                    style={props.bodyStyle  ? props.bodyStyle : {}}
                >
                    {props.body}
                </Modal.Body>
                
            </Modal>
        </>
    )
};