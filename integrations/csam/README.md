# ABOUT CSAM Integreation


## Configure

Create an Integration record in Django admin:

- Name: csam
- Description: Integration to support CSAM version 4.10
- Config:
```json
{
    "base_url": "http://csam-test.agency.gov/csam/api",
    "personal_access_token": "<personal_access_token>"
}
```
- Config schema:
```json
{}
```

For local dev and testing, create an Integration record in Django admin for CSAM mock service:

- Name: csam
- Description: Integration to support CSAM version 4.10
- Config:
```json
{
    "base_url": "http://localhost:9002",
    "personal_access_token": "FAD619"
}
```
- Config schema:
```json
{}
```

## Testing with Mock Service

The CSAM integration includes a mock CSAM service you can launch in the terminal to test your integration.

To launch the mock service do the following in a separate terminal from the root directory of GovReady-Q:

```python
pip install click
python integrations/csam/mock.py
```

## Details

Data will be stored in endpoints record with the endpoint as the reference.

TBD: How often is endpoint history clean up? Update everytime or only if information changes?

## [WIP] Field Mappings Notes

```python
system.description = get_object_or_404(Endpoint, integration=csam, endpoint_path=f'/system/{csam_system_id}').data['description']
system.name = get_object_or_404(Endpoint, integration=csam, endpoint_path=f'/system/{csam_system_id}').data['name']
```
## Testing in Browser

The following URLs will test the integration from your browser. Data will be returned from either the mock service or actual service based on integration configuration.

- URL: http://localhost:8000/integrations/csam/identify
- Purpose: Identifies the integration. All integrations have this URL.
- Returns:
```text
Attempting to communicate with csam integration: This is csam version 0.1
```

- URL: http://localhost:8000/integrations/csam/endpoint/system/111
- Purpose: Get data from an endpoint
- Returns: 
```text
Attempting to communicate with 'csam' integration: This is csam version 0.1

endpoint: /system/111

{
    "system_id": 111,
    "name": "My IT System",
    "description": "This is a simple test system"
}
```

## Pairing a System in GovReady-Q to system in CSAM

To pair a system in GovReady-Q to a system in CSAM, add the following line to the GovReady-Q's `System.info` JSONfield replacing `<csam_system_id>` with the system's CSAM ID.

```bash
{"csam_system_id": <csam_system_id>}
```

## [WIP] Updating Multiple Systems

http://localhost:8000/integrations/csam/get_multiple_system_info
TODO: Pass in multiple systems parameters

## Running the Mock Service (mock.py)

The integration's mock service consists of a simple Python webserver to simulate CSAM's API.

Start mock service in its own terminal window. *Be sure to star the mock service within the `govready-q-dev` Docker container*:

```bash
docker exec -it govready-q-dev python3 integrations/csam/mock.py
```

In a separate terminal window, `exec` into the govready-q-dev container to interact via `curl` with mock service:

```bash
docker exec -it govready-q-dev /bin/bash 
```

The following `curl` commands can be run from within the govready-q-dev container to interact with the mock service:

```bash
# Accessing mock service
curl localhost:9002/v1/test/hello
curl localhost:9002/v1/test/authenticate-test
curl localhost:9002/v1/systems/111  # Will faill because requires authentication

# Accessing mock service with authentication
curl -X 'GET' \
-H 'accept: application/json;odata.metadata=minimal;odata.streaming=true' \
-H 'Authorization: Bearer FAD619' \
'http://localhost:9002/v1/systems/111'
```

## Experimenting

```python
# Fetch previously retrieved and stored endpoint data
get_object_or_404(Endpoint, integration=csam, endpoint_path=f"/v1/system/222").data["name"]

```
