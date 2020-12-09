# Schemas

## OSCAL

* `oscal_component_schema.json`

Use the Node.js [ajv](https://ajv.js.org/) tool to validate against
the OSCAL JSON schemas.  E.g.,

```
ajv validate -s oscal_component_schema.json -d component.json --extend-refs=true --verbose
```

The source for our copy of `oscal_component_schema.json` came from
[JSON Schema for
OSCAL](https://github.com/usnistgov/OSCAL/tree/master/json/schema).
It required a couple of tweaks to actually work (I think there is a
bug in the way NIST generates JSON schemas from what I believe to be
the XML Schema "source of truth".)  Basically, the JSON schema
included many "minItems: 1" and "minProperties: 1" which should be
"minItems: 0" and "minProperties: 0".




