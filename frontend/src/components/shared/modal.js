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
                show={modalStatus}
                onHide={() => dispatch(hide())}
                aria-labelledby="react-modal"
                dialogClassName="react-modal"
            >
                <Modal.Header closeButton style={{backgroundColor: "#e5e5e5"}}>
                    <Modal.Title id="modal-title">
                        {props.header}
                    </Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    {props.body}
                </Modal.Body>
                
            </Modal>
        </>
    )
};