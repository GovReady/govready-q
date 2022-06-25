import React, { Component } from "react";
import { PropTypes } from "prop-types";
import { AsyncPaginate } from "react-select-async-paginate";
import axios from "axios";


export class MultiDropdownPaginated extends Component {
  constructor(props) {
    super(props);

    this.state = {
      selected: props.selected
    }
  }

  componentDidMount = () => {
    // console.log('mount', this.state)
  };

  componentDidUpdate = () => {
    this.props.onChange(this.state.selected);
  };

  loadOptions = async (searchQuery, loadedOptions, { page }) => {
    // console.log(searchQuery, loadedOptions, { page })
    let params = { params: { page: page, count: this.props.pageSize } };
    if (searchQuery.length) {
      params.params[this.props.filterBy] = searchQuery;
    }
    let response = await axios.get(this.props.url, params)
      .then((response) => response.data, (error) => {
        this.props.onError(error);
      });
    let options = response.data.map(obj => { return { value: obj.id, label: obj[this.props.displayKey], data: obj } });
    if (this.props.addOptionIfNoneExistFunction != null) {
      this.props.addOptionIfNoneExistFunction(options, searchQuery);
    }
    return {
      options: options,
      hasMore: response.pages.next_page != null,
      additional: {
        page: searchQuery ? 2 : page + 1,
      },
    };
  };

  setOptions = (options) => {
    this.setState({ selected: options });
  };

  render = () => {
    return (
      <AsyncPaginate
        value={this.state.selected}
        isMulti
        debounceTimeout={this.props.debounceTimeout}
        loadOptions={this.loadOptions}
        onChange={this.setOptions}
        isSearchable={true}
        placeholder={this.props.placeholder}
        additional={{
          page: 1,
        }}
      />
    );
  }

}

MultiDropdownPaginated.propTypes = {
  placeholder: PropTypes.string.isRequired,
  url: PropTypes.string.isRequired,
  selected: PropTypes.arrayOf(PropTypes.object).isRequired,
  onChange: PropTypes.func.isRequired,
  addOptionIfNoneExistFunction: PropTypes.func,
  onError: PropTypes.func.isRequired,
  filterBy: PropTypes.string.isRequired,
  pageSize: PropTypes.number,
  debounceTimeout: PropTypes.number,
  displayKey: PropTypes.string.isRequired
};

MultiDropdownPaginated.defaultProps = {
  pageSize: 20,
  debounceTimeout: 300,
  addOptionIfNoneExistFunction: null
};
