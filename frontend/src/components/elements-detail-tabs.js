import React from 'react';
import { MultiDropdownPaginated } from "./shared/multi-dropdown-paginated";
import * as ReactDOM from "react-dom";

// class ElementTags extends Component {
//     constructor(props) {
//         super(props);
//     }
//
//     onChange(selected) {
//         console.log(selected)
//     };
//
//     render() {
//         return <span className="component-tag">{{tag.label}}</span>
//     }
// }

class ElementTagsEdit extends React.Component {
    constructor(props) {
        super(props);
    }

    onChange(selected) {
        console.log('set tags to these ids', selected.map(item => item.data.id))
    };

    onError(event) {
        console.log(event);
    }

    render() {
        return <MultiDropdownPaginated
            placeholder='Select Tags'
            url='/api/v2/tags/'
            filterBy='label__istartswith'
            pageSize={20}
            onChange={this.onChange}
            onError={this.onError}
            selected={[]} />
    }
}

function renderElementTags() {
    ReactDOM.render(<ElementTagsEdit />, document.getElementById('edit-tags'));
    // ReactDOM.render(<MultiDropdownPaginated />, document.getElementById('edit-tags'));
}

// This is a hack to get it to work with existing django templates.
window.renderElementTags = renderElementTags;
