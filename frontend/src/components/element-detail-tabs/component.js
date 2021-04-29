import React from 'react';
import { MultiDropdownPaginated } from "../shared/multi-dropdown-paginated";
import * as ReactDOM from "react-dom";
import { PropTypes } from "prop-types";
import { componentTagsStateSlice } from "./slice"
import { Provider } from "react-redux";
import store from "./../../store";
import { useSelector, useDispatch } from 'react-redux'
const { setTags } = componentTagsStateSlice.actions;
import { Tag } from '@trussworks/react-uswds'

const ElementTags = () => {
    const tags = useSelector((state) => state.componentTags.value);

    return (
        <div>
            {tags.map(tag => <Tag key={tag.id}>{tag.label}</Tag>)}
        </div>
    )
};

const ElementTagsEdit = ({ tags }) => {
    tags = tags.map(tag => { return { label: tag.label, value: tag.id, data: tag } });
    const dispatch = useDispatch();

    let onChange = (selected) => {
        dispatch(setTags(selected.map(item => item.data)));
        console.log('set tags to these ids', selected.map(item => item.data.id))
    };

    let onError = (event) => {
        console.log(event);
    };

    return (
        <MultiDropdownPaginated
            placeholder='Select Tags'
            url='/api/v2/tags/'
            filterBy='label__istartswith'
            displayKey='label'
            pageSize={20}
            onChange={onChange}
            onError={onError}
            selected={tags} />
    )
};

ElementTagsEdit.propTypes = {
    tags: PropTypes.arrayOf(PropTypes.object).isRequired
};


function renderElementTags(existingTags) {
    store.dispatch(setTags(existingTags));

    ReactDOM.render(
        <Provider store={store}>
            <ElementTagsEdit tags={existingTags} />
        </Provider>,
        document.getElementById('edit-tags')
    );

    ReactDOM.render(
        <Provider store={store}>
            <ElementTags />
        </Provider>,
        document.getElementById('show-tags')
    );


}

// This is a hack to get it to work with existing django templates.
window.renderElementTags = renderElementTags;
