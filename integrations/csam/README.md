# ABOUT CSAM Integreation

A simple Python webserver to generate mock CSAM API
results

Usage:
   

```
# Start mock service
python3 integrations/csam/mock.py
```

```
# Accessing mock service
curl localhost:9002/endpoint
curl localhost:9002/hello
curl localhost:9002/system/111  # requires authentication
```



```
# Accessing mock service with authentication
 curl -X 'GET' 'http://localhost:9002/system/111' \
 -H 'accept: application/json;odata.metadata=minimal;odata.streaming=true' \
 -H 'Authorization: Bearer FAD619'
```

