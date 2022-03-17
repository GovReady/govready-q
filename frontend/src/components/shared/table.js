/* eslint-disable no-unused-vars */
/* eslint-disable react-hooks/exhaustive-deps */

import React, { useEffect, useState } from "react";
import PropTypes from "prop-types";
import TablePagination from '@mui/material/TablePagination';
import TextField from '@mui/material/TextField';
import { useDebouncedCallback } from "use-debounce";
import '../../../clientStyles.css'
import {
  Table,
  Row,
  Grid,
  Col,

}
  from 'react-bootstrap';

export const columnDataTypes = {
  STRING: 1,
  TIMESTAMP: 2,
  STATUS: 3,
  BOOL: 4,
};



export const DataTable = (props) => {
  const formatOrderBy = (data) => {
    return `${data[1] === "desc" ? "-" : ""}${data[0]}`;
  };

  const [querystrings, setQuerystrings] = useState({
    orderBy: formatOrderBy(props.sortby),
    search: "",
    page: 1,
    count: 10,
    // rollup: true
  });
  const [columns, setColumns] = useState(props.columns);
  const [sorting, setSorting] = useState(props.sortby);

  const [response, setResponse] = useState({ data: [], rollup: {} });
  const debounceDuration = 250;


  useEffect(() => {
    debouncedFetch(querystrings);
  }, [querystrings]);

  const error = false;
  const fetch = (args) => {
    if (props.rollups.length > 0) {
      args.rollup = "true";
    }
    let cleanedArgs = {};
    Object.keys(args).forEach((prop) => {
      if (typeof args[prop] === "string") {
        if (args[prop].length > 0) {
          cleanedArgs[prop] = args[prop];
        }
      } else {
        cleanedArgs[prop] = args[prop];
      }
    });
    return props.endpoint(cleanedArgs).then((resp) => {
      setResponse(resp.data);
      props.onResponse(resp.data);
    });
  };

  const debouncedFetch = useDebouncedCallback((args) => {
    fetch(args);
  }, debounceDuration);

  if (error) {
    return <pre>{error.toString()}</pre>;
  }

  const handlePageChange = (event, page) => {
    setQuerystrings({ ...querystrings, page: page + 1 }); // starts at 0, but backend starts at 1
  };
  const handleRowsPerPageChange = (event) => {
    setQuerystrings({ ...querystrings, count: event.target.value });
  };
  const handleSetSorting = (str) => {
    if (str !== 'undefined') {
      let sortTmp = [str, sorting[1] === "desc" ? "asc" : "desc"];
      setSorting(sortTmp);
      setQuerystrings({ ...querystrings, orderBy: formatOrderBy(sortTmp) });
    }
  };

  const doSearch = (val) => {
    setQuerystrings({ ...querystrings, search: val, page: 1 });
  };

  const getValue = (obj, str) => {
    str = str.replace(/\[(\w+)\]/g, ".$1"); // convert indexes to properties
    str = str.replace(/^\./, ""); // strip a leading dot
    const a = str.split(".");
    for (let i = 0, n = a.length; i < n; ++i) {
      let k = a[i];
      if (k in obj) {
        obj = obj[k];
      } else {
        return;
      }
    }
    return obj;
  };
  
  return (
    <div className="panel-body">
      <Grid>
        <Grid>
          <Row
            style={{
              background: "#eee",
              height: "46.42px",
              borderTopLeftRadius: "4px",
              borderTopRightRadius: "4px",
              border: "1px solid #bbb",
              width: '1241.330px',
              marginLeft: "-65px"
            }}
          >
            <Col
              md={6}
              style={{
                marginTop: "10px",
                padding: "0px 0px",
              }}
            >
              {props.header.props.children}
            </Col>
            <Col md={6}
              style={{
                padding: '0px 0px'
              }} >
            </Col>
          </Row>
        </Grid>
        <Grid
          style={{
            borderLeft: "1px solid #bbb",
            borderRight: "1px solid #bbb",
            borderBottom: "1px solid #bbb",
            width: '1241.330px',
            marginLeft: '-50px'
          }}
        >
          <Row>
            {props.searchEnabled && (
              <>
                <TextField
                  style={{ width: '96.5%', marginLeft: '20px' }}
                  inputProps={{ style: { fontSize: 20 } }} // font size of input text
                  InputLabelProps={{ style: { fontSize: 20 } }} // font size of input label
                  variant="standard"
                  label="Search"
                  size="medium"
                  fullWidth={true}
                  onChange={(e) => doSearch(e.target.value)}
                />
                <Table hover condensed responsive>
                  <tbody>
                    {response.data &&
                      response.data.map((obj, i) => (
                        <tr key={i}>
                          {columns.map((col, index) => {
                            return (
                              <td key={index}>
                                <span style={{
                                  marginLeft: "15px",
                                  display: 'flex'
                                }}
                                >{col.renderCell(obj)}</span>
                              </td>
                            )
                          })}
                        </tr>
                      ))}
                  </tbody>
                </Table>
                <TablePagination
                  style={{ fontSize: "15px" }}
                  component="div"
                  count={
                    response.pages?.total_records ? response.pages?.total_records : 0
                  }
                  onPageChange={handlePageChange}
                  onRowsPerPageChange={handleRowsPerPageChange}
                  page={querystrings.page - 1}
                  rowsPerPage={querystrings.count}
                  rowsPerPageOptions={[5, 10, 25, 50, 100]}
                />
              </>
            )}
          </Row>
        </Grid>
      </Grid>
    </div>
    
  );
};

DataTable.defaultProps = {
  searchEnabled: true,
  rollups: [],
};

DataTable.propTypes = {
  className: PropTypes.string,
  endpoint: PropTypes.func.isRequired,
  columns: PropTypes.array.isRequired,
  sortby: PropTypes.array.isRequired,
  searchEnabled: PropTypes.bool,
  onRowClick: PropTypes.func,
};

export default DataTable;