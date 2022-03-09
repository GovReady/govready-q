import React, { useRef, useState } from 'react';
import { MultiDropdownPaginated } from "./multi-dropdown-paginated";
import { PropTypes } from "prop-types";
import { useDispatch } from 'react-redux';
import axios from "axios";
import { isEqual } from 'lodash';


export const TagDropdown = ({ updateTagsURL, action, existingTags }) => {

    const dispatch = useDispatch();
    const dropdownRef = useRef();
    const newItemSuffix = " (NEW)";

    const tagURL = `/api/v2/tags/`;

    const convertObjectsToOptions = (data) => {
        return data.map(tag => { return { label: tag.label, value: tag.id, data: tag } })
    };
    const [state, setState] = useState(convertObjectsToOptions(existingTags));

    const updateTags = async (tagIds, selected) => await axios.put(updateTagsURL, { tag_ids: Array.from(tagIds) })
        .then((response) => {
            setState(selected);
            dispatch(action(selected.map(item => item.data))); // Dispatch if success
            return response.data;
        }, (error) => {
            dropdownRef.current.setOptions(state);
            throw new Error(error);
        });

    const createTag = async (selected) => {
        if (selected.length) {
            let createOption = selected[selected.length - 1];
            if (!Object.keys(createOption.data).length) {
                createOption.label = createOption.label.replace(newItemSuffix, "");
                return await axios.post(tagURL, { label: createOption.value })
                    .then((response) => {
                        return response.data;
                    }, (error) => {
                        dropdownRef.current.setOptions(state);
                        throw new Error(error);
                    });
            }
        }
    };

    const addOptionIfNotExists = (options, searchQuery) => {
        if (searchQuery.length) {
            let exists = options.find(option => option.label.toUpperCase() == searchQuery.toUpperCase());
            if (exists == undefined) {
                options.push({ value: searchQuery, label: `${searchQuery}${newItemSuffix}`, data: {} })
            }
        }

    };

    const onChange = (selected) => {
        let tagIds = selected.map(x => x.data.id).sort();
        let previousIds = state.map(x => x.data.id).sort();
        // Checking & Storing previous and current Tags in case of an exception.  Then reverting state if necessary
        // console.log(tagIds, previousIds, !isEqual(tagIds, previousIds))
        if (!isEqual(tagIds, previousIds)) {
            createTag(selected)
                .then(tag => { if (tag != undefined) selected[selected.length - 1] = convertObjectsToOptions([tag])[0]; })
                .then(() => {
                    let tagIds = selected.map(x => x.data.id).sort();
                    return updateTags(tagIds, selected);
                })
                .catch((error) => onError(error));
        }
    };

    let onError = (event) => {
        console.log(event); // todo - banner
    };

    return (
        <div>
            <label>Tags</label>
            <MultiDropdownPaginated
                ref={dropdownRef}
                placeholder='Select Tags'
                url={tagURL}
                filterBy='label__istartswith'
                displayKey='label'
                addOptionIfNoneExistFunction={addOptionIfNotExists}
                pageSize={20}
                onChange={onChange}
                onError={onError}
                selected={state} />
        </div>

    )
};

TagDropdown.defaultProps = {
  existingTags: []
};

TagDropdown.propTypes = {
    updateTagsURL: PropTypes.string.isRequired,
    action: PropTypes.func.isRequired,
    existingTags: PropTypes.arrayOf(PropTypes.object).isRequired
};
