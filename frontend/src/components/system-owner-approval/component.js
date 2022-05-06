import React, {useState} from 'react';
import ReactDOM from 'react-dom';
import {v4 as uuid_v4} from "uuid";
import { RequireApprovalModal } from './requireApprovalModal';
import { ProposalSteps } from './proposal-steps';
import { Provider } from "react-redux";
import store from "../../store";

window.requireApprovalModal = ( userId, systemId, systemName, elementId, require_approval ) => {
    const uuid = uuid_v4();
    ReactDOM.render(
        <Provider store={store}>
            <RequireApprovalModal userId={userId} systemId={systemId} systemName={systemName} elementId={elementId} require_approval={require_approval} uuid={uuid} />
        </Provider>,
        document.getElementById('private-component-modal')
    );
};

window.proposalSteps = ( userId, system, element, proposal, request, hasSentRequest ) => {
    ReactDOM.render(
        <Provider store={store}>
            <ProposalSteps userId={userId} system={system} element={element} proposal={proposal} request={request} hasSentRequest={hasSentRequest} />
        </Provider>,
        document.getElementById('system-owner-proposal-steps')
    );
};