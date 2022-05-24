# ABOUT GRC Integreation


## Configure

Create an Integration record in Django admin:

- Name: csam
- Description: Integration to support Generic GRC based on CSAM version 4.10
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

For local dev and testing, create an Integration record in Django admin for GRC mock service:

- Name: csam
- Description: Integration to support GRC version 4.10
- Config:
```json
{
    "base_url": "http://localhost:9022",
    "personal_access_token": "FAD619",
}
```
- Config schema:
```json
{}
```

## Details

Data will be stored in endpoints record with the endpoint as the reference.

TBD: How often is endpoint history clean up? Update everytime or only if information changes?

## [WIP] Field Mappings Notes

```python
system.description = get_object_or_404(Endpoint, integration=grc, endpoint_path=f'/system/{grc_system_id}').data['description']
system.name = get_object_or_404(Endpoint, integration=grc, endpoint_path=f'/system/{csam_system_id}').data['name']
```
## Testing in Browser

The following URLs will test the integration. Data will be returned from either the mock service or actual service based on integration configuration.

- URL: http://localhost:8000/integrations/grc/identify 
- Purpose: Identifies the integration. All integrations have this URL.
- Returns:
```text
Attempting to communicate with grc integration: This is grc version 0.1
```

- URL: http://localhost:8000/integrations/grc/endpoint/system/111
- Purpose: Get data from an endpoint
- Returns: 
```text
Attempting to communicate with 'grc' integration: This is grc version 0.1

endpoint: /v1/system/111

{
    "system_id": 111,
    "name": "My IT System",
    "description": "This is a simple test system"
}
```

## Pairing a System in GovReady-Q to system in GRC

To pair a system in GovReady-Q to a system in GRC, add the following line to the GovReady-Q's `System.info` JSONfield replacing `<csam_system_id>` with the system's GRC ID.

```bash
{"csam_system_id": <csam_system_id>}
```

## [WIP] Updating Multiple Systems

http://localhost:8000/integrations/csam/get_multiple_system_info
TODO: Pass in multiple systems parameters

## Running the Mock Service (mock.py)

The integration's mock service consists of a simple Python webserver to simulate GRC's API.

Start mock service in its own terminal window:

```bash
docker exec -it govready-q-dev python3 integrations/grc/mock.py
```

In a separate terminal window, `exec` into the govready-q-dev container to interact via `curl` with mock service:

```bash
docker exec -it govready-q-dev /bin/bash 
```

The following `curl` commands can be run from within the govready-q-dev container to interact with the mock service:

```bash
# Accessing mock service
curl localhost:9022/v1/test/hello
curl localhost:9022/v1/system/111  # requires authentication

# Accessing mock service with authentication
 curl -X 'GET' 'http://localhost:9022/v1/system/111' \
 -H 'accept: application/json;odata.metadata=minimal;odata.streaming=true' \
 -H 'Authorization: Bearer FAD619'
```

## Experimenting

```python
# Fetch previously retrieved and stored endpoint data
get_object_or_404(Endpoint, integration=grc, endpoint_path=f"/v1/system/222").data["name"]

```
