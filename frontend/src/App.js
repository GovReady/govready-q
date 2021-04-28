import React, { useState } from "react";
import Select from "react-select";
import SelectAsyncPaginate from "./SelectAsyncPaginate";
import { Container, Col, Form, FormGroup, Label } from "reactstrap";

function App() {
  const options = [
    { value: "The Crownlands" },
    { value: "Iron Islands" },
    { value: "The North" },
    { value: "The Reach" },
    { value: "The Riverlands" },
    { value: "The Vale" },
    { value: "The Westerlands" },
    { value: "The Stormlands" },
  ];

  const [region, setRegion] = useState(options[0]);
  const [currentCountry, setCurrentCountry] = useState(null);
  const onchangeSelect = (item) => {
    setCurrentCountry(null);
    setRegion(item);
  };

  return (
    <div className="App">
      <Container className="content">
        <Form className="mt-5">
          <FormGroup row>
            <Label for="region" sm={1}>
              Region
            </Label>
            <Col sm={8}>
              <Select
                value={region}
                onChange={onchangeSelect}
                options={options}
                getOptionValue={(option) => option.value}
                getOptionLabel={(option) => option.value}
              />
            </Col>
          </FormGroup>
          <FormGroup row>
            <Label for="region" sm={1}>
              House
            </Label>
            <Col sm={8}>
              <SelectAsyncPaginate
                regionName={region.value}
                value={currentCountry}
                onChange={(country) => setCurrentCountry(country)}
              />
            </Col>
          </FormGroup>
        </Form>
      </Container>
    </div>
  );
}

export default App;