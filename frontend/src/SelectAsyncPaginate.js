import React, { useEffect, useState } from "react";
import PropTypes from "prop-types";
import { AsyncPaginate } from "react-select-async-paginate";

const SelectAsyncPaginate = (props) => {
  const [regionName, setRegionName] = useState(null);

  useEffect(() => {
    setRegionName(props.regionName);
  }, [props.regionName]);

  const loadOptions = async (searchQuery, loadedOptions, { page }) => {

    console.log(`loading page:${page} - limit: 10`);

    const response = await fetch(
      `https://www.anapioficeandfire.com/api/houses?region=${regionName}&page=${page}&pageSize=10`
    );
    const responseJSON = await response.json();

    return {
      options: responseJSON,
      hasMore: responseJSON.length >= 1,
      additional: {
        page: searchQuery ? 2 : page + 1,
      },
    };
  };

  const onChange = (option) => {
    if (typeof props.onChange === "function") {
      props.onChange(option);
    }
  };

  return (
    <AsyncPaginate
      key={JSON.stringify(regionName)}
      value={props.value || ""}
      loadOptions={loadOptions}
      getOptionValue={(option) => option.name}
      getOptionLabel={(option) => option.name}
      onChange={onChange}
      isSearchable={false}
      placeholder="Select House"
      additional={{
        page: 1,
      }}
    />
  );
};

SelectAsyncPaginate.propTypes = {
  regionName: PropTypes.string.isRequired,
  value: PropTypes.object,
  onChange: PropTypes.func,
};

export default SelectAsyncPaginate;