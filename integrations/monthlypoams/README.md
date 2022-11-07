## Configure

Create an Integration record in Django admin:

Name: monthlypoams
Description: Integration to support monthlypoams version 4.10
Config:

    {"base_url": "http://monthlypoams-test.agency.gov/monthlypoams/api", "personal_access_token": "<personal_access_token>"}

Config schema:

    {}

For local dev and testing, create an Integration record in Django admin for monthlypoams mock service:

Name: monthlypoams
Description: Monthly POA&Ms review
Config:

    {"base_url": "http://localhost:9042", "personal_access_token": "FAD619"}

Config schema:

    {}

## Details

Data will be stored in endpoints record with the endpoint as the reference.

## [WIP] Field Mappings Notes

    system.description = get_object_or_404(Endpoint, integration=monthlypoams, endpoint_path=f'/system/{monthlypoams_system_id}').data['description']

    system.name = get_object_or_404(Endpoint, integration=monthlypoams, endpoint_path=f'/system/{monthlypoams_system_id}').data['name']

## Testing with Mock Service

The integration includes a mock service you can launch in the terminal to test your integration. The integration's mock service uses a simple Python webserver to simulating the API.

Start mock service in its own terminal window. *Be sure to star the mock service within the `govready-q-dev` Docker container*:

    docker exec -it govready-q-dev python3 integrations/monthlypoams/mock/mock.py

In a separate terminal window interact via `curl` with mock service:

    docker exec -it govready-q-dev python3 curl localhost:9002/v1/test/hello

    docker exec -it govready-q-dev python3 curl localhost:9002/v1/test/authenticate-test

    docker exec -it govready-q-dev python3 curl -X 'GET' \
    -H 'accept: application/json;odata.metadata=minimal;odata.streaming=true' \
    -H 'Authorization: Bearer FAD619' \
    'http://localhost:9002/v1/test/authenticate-test'

    docker exec -it govready-q-dev python3 curl localhost:9002/v1/systems/111  # Will faill because requires authentication

    docker exec -it govready-q-dev python3 curl -X 'GET' \
    -H 'accept: application/json;odata.metadata=minimal;odata.streaming=true' \
    -H 'Authorization: Bearer FAD619' \
    'http://localhost:9002/v1/systems/111'

## Testing

The following URLs will test the integration. Data will be returned from either the mock service or actual service based on integration configuration.

URL: http://localhost:8000/integrations/monthlypoams/identify
Purpose: Identifies the integration. All integrations have this URL.

URL: http://localhost:8000/integrations/monthlypoams/endpoint/system/111
Purpose: Get data from an endpoint

## Pairing a System in GovReady-Q to system in monthlypoams

To pair a system in GovReady-Q to a system in monthlypoams, add the following line to the GovReady-Q's `System.info` JSONfield replacing `<monthlypoams_system_id>` with the system's monthlypoams ID.

    {"monthlypoams_system_id": <monthlypoams_system_id>}

## [WIP] Retrieving Multiple Systems

http://localhost:8000/integrations/monthlypoams/get_multiple_system_info
TODO: Pass in multiple systems parameters

