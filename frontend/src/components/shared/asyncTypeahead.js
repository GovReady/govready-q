import React, { useState, useEffect } from "react";
import Input from "@mui/material/Input";
import InputLabel from "@mui/material/InputLabel";
import InputAdornment from "@mui/material/InputAdornment";
import FormControl from "@mui/material/FormControl";
import GroupAddIcon from "@mui/icons-material/GroupAdd";
import { AsyncTypeahead } from "react-bootstrap-typeahead";
import "react-bootstrap-typeahead/css/Typeahead.css";
import MenuItem from "@mui/material/MenuItem";
import { makeStyles } from "@mui/styles";
import "react-bootstrap-typeahead/css/Typeahead.css";

const PER_PAGE = 50;

const useStyles = makeStyles((theme) => ({
  menuItem: {
    zIndex: 1,
    background: "whitesmoke",
    borderBottom: "1px solid black",
    "&:hover": {
      color: "#fff",
      background: "grey",
      fontSize: "12px"
    },
  },
  username: {
    fontSize: "small",
    marginLeft: "1rem",
    fontSize: "12px"
  },
}));

function makeAndHandleRequest(endpoint, order, query, excludeIds, page = 1) {
  return endpoint({
    search: query,
    page: page,
    ordering: order,
    exclude: excludeIds.join(","),
  }).then((resp) => {
    let options = resp.data.data;
    let total_count = resp.data.pages.total_records;
    return { options, total_count };
  });
}

export const AsyncPagination = ({ endpoint, order, onSelect, excludeIds, searchBarLength, placeholder, primaryKey, secondarykey }) => {
  const [state, setState] = useState({
    isLoading: false,
    options: [],
    query: "",
    excludeIds: excludeIds,
  });
  const [cache, setCache] = useState({});
  const [selected, setSelected] = useState([]);
  const classes = useStyles();

  useEffect(() => {
    setState((prev) => ({ ...prev, excludeIds: excludeIds }));
  }, [excludeIds]);

  const onSelected = (selected) => {
    setSelected([]);
    onSelect(selected);
  };

  const handleInputChange = (query) => {
    setState((prev) => ({ ...prev, query: query }));
    handleSearch(query);
  };

  const handlePagination = (e, shownResults) => {
    const { query } = state;
    const cachedQuery = cache[query];

    // Don't make another request if:
    // - the cached results exceed the shown results
    // - we've already fetched all possible results
    // if (
    //   cachedQuery.options.length > shownResults ||
    //   cachedQuery.options.length === cachedQuery.total_count
    // ) {
    //   return;
    // }
    setState((prev) => ({ ...prev, isLoading: true }));

    const page = cachedQuery.page + 1;

    makeAndHandleRequest(endpoint, order, query, state.excludeIds, page).then(
      (resp) => {
        const options = cachedQuery.options.concat(resp.options);
        cache[query] = { ...cachedQuery, options, page };
        setState((prev) => ({ ...prev, isLoading: false, options }));
      }
    );
  };

  const handleSearch = (query) => {
    // if (cache[query]) {
    //   setState((prev) => ({ ...prev, options: cache[query].options }));
    //   return;
    // }

    setState((prev) => ({ ...prev, isLoading: true }));
    makeAndHandleRequest(endpoint, order, query, state.excludeIds).then(
      (resp) => {
        cache[query] = { ...resp, page: 1 };
        setState((prev) => ({
          ...prev,
          isLoading: false,
          options: resp.options,
        }));
      }
    );
  };

  return (
    <AsyncTypeahead
      {...state}
      id="user-lookup-async-pagination"
      labelKey={primaryKey}
      isLoading={state.isLoading}
      maxResults={PER_PAGE - 1}
      minLength={2}
      style={{ width: "100%", zIndex: 1 }}
      onInputChange={handleInputChange}
      onPaginate={handlePagination}
      onSearch={handleSearch}
      onChange={onSelected}
      selected={selected}
      promptText={""}
      filterBy={() => true}
      paginate
      placeholder={placeholder}
      renderInput={({ inputRef, referenceElementRef, ...inputProps }) => (
        <FormControl variant="standard" style={{ width: searchBarLength }}>
          <Input
            {...inputProps}
            ref={(input) => {
              // Be sure to correctly handle these refs. In many cases, both can simply receive
              // the underlying input node, but `referenceElementRef can receive a wrapper node if
              // your custom input is more complex (See TypeaheadInputMulti for an example).
              inputRef(input);
              referenceElementRef(input);
            }}
            id="input-with-icon-adornment"
            fullWidth={true}
            startAdornment={
              <InputAdornment position="start">
                <GroupAddIcon sx={{ fontSize: 20 }} />
              </InputAdornment>
            }
            sx={{ fontSize: '14px' }}
          />
        </FormControl>
      )}
      renderMenuItemChildren={(option) => (
        <MenuItem
          className={classes.menuItem}
          key={option.id}
          value={option.id}
        >
          
          <span className={classes.username}>{option[primaryKey]}</span>
          <span className={classes.username}>({option[secondarykey]})</span>
        </MenuItem>
      )}
      useCache={false}
    />
  );
};
