# dicom-fhir-converter
This project was originally forked from [alexa-ian/dicom-fhir-converter](https://github.com/alexa-ian/dicom-fhir-converter). However, due to extensive refactoring and structural changes, it has since been detached from the upstream repository and is now maintained as an independent, standalone Python library.

The library converts DICOM data into a FHIR transaction Bundle that includes an ImagingStudy resource, a Patient resource, a Device resource, and optionally Observation resources. It supports two input modes: either a directory containing DICOM files (recursively parsed), or an `AsyncGenerator[dict, None]` of DICOM JSON dicts instances passed directly to the API.

This library utilizes the following projects:
- fhir.resources project (https://pypi.org/project/fhir.resources/) - used to create FHIR models
- pydicom (https://pydicom.github.io/) - (partially) used to read dicom instances

Compared to the original project, the dependency on pydicom has been reduced and the library now uses its own DicomJsonProxy class to process DICOM JSON data. This allows for more lenient and efficient parsing of DICOM data when it is already in JSON format, and avoids the somewhat stringent checks of DICOM tags not used by pydicom anyway.

The library also works internally with [Asynchronous Generators](https://superfastpython.com/asynchronous-generators-in-python/), which can increase the complexity of handling the library somewhat, but is considerably more memory-efficient, especially for extensive studies with sometimes 1000 or more DICOM instances.

## Installation

```shell
pip install dicom2fhir
```

## Usage

Parse from a directory containing DICOM files:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from dicom2fhir.dicom2fhir import from_directory
from pprint import pprint
import asyncio

# Some directory containing DICOM files (recursively parsed)
dcmDir = os.path.join("some", "directory", "with", "dicom-files")

# Configuration for the dicom2fhir conversion
dicom2fhir_config = {
    "dicom_timezone": "Europe/Berlin",  # Set the timezone for DICOM dates
    "generator": {
        "imaging_study": {
            "add_instances": False  # Do not add single instances, only series to the ImagingStudy
        },
        "observation": {
            "add_vital_signs": True  # Add vital signs Observations for body weight and height
        }
    }
}

# Async wrapper
async def main():
    # Convert to FHIR Bundle
    bundle = await from_directory(dcmDir, config=dicom2fhir_config)

    # Print the resulting FHIR Bundle as JSON
    pprint(bundle.model_dump_json(indent=2))

if __name__ == "__main__":
    asyncio.run(main())
```

Parse from an iterable of DICOM JSON dicts:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from dicom2fhir.dicom2fhir import from_generator
from pprint import pprint
import asyncio

# Configuration for the dicom2fhir conversion
dicom2fhir_config = {
    "dicom_timezone": "Europe/Berlin",  # Set the timezone for DICOM dates
    "generator": {
        "imaging_study": {
            "add_instance": False  # Do not add single instances, only series to the ImagingStudy
        },
        "observation": {
            "add_vital_signs": True  # Add vital signs Observations for body weight and height
        }
    }
}

# Dummy async generator function to simulate DICOM JSON dicts
async def async_get_dicom_json_generator():
    yield {
        # A minimal valid DICOM-to-FHIR dictionary structure (example content)
        "00080020": {"vr": "DA", "Value": ["20210101"]},
        "00100010": {"vr": "PN", "Value": [{"Alphabetic": "Doe^John"}]},
    }

# Main coroutine to run the conversion
async def main():
    dicom_json_dicts = async_get_dicom_json_generator()

    # Convert to FHIR Bundle
    bundle = await from_generator(dicom_json_dicts, config=dicom2fhir_config)

    # Print the resulting FHIR Bundle as JSON
    pprint(bundle.model_dump_json(indent=2))

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())
```

Apart from the above configuration options you can also pass a custom function via `config['id_function']` to create FHIR resource ids from business identifiers. This is useful if you want to use a different identifier scheme than the default one, which is based on the DICOM Study UID. Please see the [default id function](/dicom2fhir/helpers.py#L36) for reference.


The resulting object is a FHIR R4B transaction [Bundle](https://hl7.org/fhir/R4B/bundle.html) containing:
-	One [ImagingStudy](https://hl7.org/fhir/R4B/imagingstudy.html) resource
-	One [Patient](https://hl7.org/fhir/R4B/patient.html) resource
-	One [Device](https://hl7.org/fhir/R4B/device.html) resource
-	Optionally, [Observation](https://hl7.org/fhir/R4B/observation.html) resources for body weight and height if the corresponding DICOM tags are present.

If you need to update the bodysite Snomed mappings run:

```bash
cd dicom2fhir 
./build_terminologies.py
```

Activate tests against Firemetrics:
```bash
export RUN_FMX_TESTS=1
```

## Structure 
The FHIR Imaging Study id is being generated internally within the library. 
The DICOM Study UID is actually stored as part of the "identifier" (see ```"system":"urn:dicom:uid"``` object for DICOM study uid.

### Sample Output
```json
{
  "resourceType": "Bundle",
  "id": "f87746a0-7ff5-4666-8302-423cfdf3f275",
  "type": "transaction",
  "entry": [
    {
      "fullUrl": "urn:uuid:7423de5ec8508bb1dc9036a7478d7bd4940a6c5daf5751d8ad2ca13f1dae85d0",
      "resource": {
        "resourceType": "ImagingStudy",
        "id": "7423de5ec8508bb1dc9036a7478d7bd4940a6c5daf5751d8ad2ca13f1dae85d0",
        "identifier": [
          {
            "use": "usual",
            "type": {
              "coding": [
                {
                  "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                  "code": "ACSN"
                }
              ]
            },
            "value": "62541999"
          },
          {
            "system": "urn:dicom:uid",
            "value": "urn:oid:1.2.840.113711.9425041.6.7312.599853596.26.2116281012.165600"
          }
        ],
        "status": "available",
        "modality": [
          {
            "system": "http://dicom.nema.org/resources/ontology/DCM",
            "code": "CR"
          }
        ],
        "subject": {
          "reference": "Patient/c13a8cd37541b87b256fe08a3800b5f409439357a250661efaec6a9642901d72"
        },
        "started": "2020-01-11T00:00:00",
        "numberOfSeries": 4,
        "numberOfInstances": 4,
        "procedureCode": [
          {
            "coding": [
              {
                "system": "UNKNOWN",
                "code": "7003520",
                "display": "XR Ribs w/ PA Chest Left"
              }
            ],
            "text": "XR Ribs w/ PA Chest Left"
          }
        ],
        "series": [
          {
            "uid": "1.2.840.113564.19216812.20200110232537925600",
            "number": 2,
            "modality": {
              "system": "http://dicom.nema.org/resources/ontology/DCM",
              "code": "CR"
            },
            "description": "AP",
            "numberOfInstances": 1,
            "bodySite": {
              "code": "RIBS",
              "userSelected": true
            },
            "instance": [
              {
                "uid": "1.2.840.113564.19216812.20200110232537925610.2203801020003",
                "sopClass": {
                  "system": "urn:ietf:rfc:3986",
                  "code": "urn:oid:1.2.840.10008.5.1.4.1.1.1"
                },
                "number": 1,
                "title": "DERIVED\\PRIMARY"
              }
            ]
          },
          {
            "uid": "1.2.840.113564.19216812.20200110232537987660",
            "number": 5,
            "modality": {
              "system": "http://dicom.nema.org/resources/ontology/DCM",
              "code": "CR"
            },
            "description": "RPO",
            "numberOfInstances": 1,
            "bodySite": {
              "code": "RIBS",
              "userSelected": true
            },
            "instance": [
              {
                "uid": "1.2.840.113564.19216812.20200110232537987670.2203801020003",
                "sopClass": {
                  "system": "urn:ietf:rfc:3986",
                  "code": "urn:oid:1.2.840.10008.5.1.4.1.1.1"
                },
                "number": 1,
                "title": "DERIVED\\PRIMARY"
              }
            ]
          },
          {
            "uid": "1.2.840.113564.19216812.20200110232538003680",
            "number": 6,
            "modality": {
              "system": "http://dicom.nema.org/resources/ontology/DCM",
              "code": "CR"
            },
            "description": "LPO",
            "numberOfInstances": 1,
            "bodySite": {
              "code": "RIBS",
              "userSelected": true
            },
            "instance": [
              {
                "uid": "1.2.840.113564.19216812.20200110232538003690.2203801020003",
                "sopClass": {
                  "system": "urn:ietf:rfc:3986",
                  "code": "urn:oid:1.2.840.10008.5.1.4.1.1.1"
                },
                "number": 1,
                "title": "DERIVED\\PRIMARY"
              }
            ]
          },
          {
            "uid": "1.2.840.113564.19216812.20200110232537909580",
            "number": 1,
            "modality": {
              "system": "http://dicom.nema.org/resources/ontology/DCM",
              "code": "CR"
            },
            "description": "PA",
            "numberOfInstances": 1,
            "bodySite": {
              "system": "http://snomed.info/sct",
              "code": "43799004",
              "display": "Chest"
            },
            "instance": [
              {
                "uid": "1.2.840.113564.19216812.20200110232537909590.2203801020003",
                "sopClass": {
                  "system": "urn:ietf:rfc:3986",
                  "code": "urn:oid:1.2.840.10008.5.1.4.1.1.1"
                },
                "number": 1,
                "title": "DERIVED\\PRIMARY"
              }
            ]
          }
        ]
      },
      "request": {
        "method": "PUT",
        "url": "ImagingStudy/7423de5ec8508bb1dc9036a7478d7bd4940a6c5daf5751d8ad2ca13f1dae85d0"
      }
    },
    {
      "fullUrl": "urn:uuid:c13a8cd37541b87b256fe08a3800b5f409439357a250661efaec6a9642901d72",
      "resource": {
        "resourceType": "Patient",
        "id": "c13a8cd37541b87b256fe08a3800b5f409439357a250661efaec6a9642901d72",
        "identifier": [
          {
            "use": "usual",
            "system": "urn:dicom:patient-id",
            "value": "A09650600b71bfe4043b5b44e05b362015f"
          }
        ],
        "name": [
          {
            "family": "Doe",
            "given": ["John", "A."],
            "prefix": "Dr.",
            "suffix": "MD"
          }
        ],
        "gender": "male",
        "birthDate": "1976-01-01"
      },
      "request": {
        "method": "PUT",
        "url": "Patient/c13a8cd37541b87b256fe08a3800b5f409439357a250661efaec6a9642901d72"
      }
    },
    {
      "fullUrl": "urn:uuid:5a4d77e9-04a7-4897-ad05-b80432794242",
      "resource": {
        "resourceType": "Device",
        "id": "5a4d77e9-04a7-4897-ad05-b80432794242",
        "manufacturer": "Carestream Health",
        "deviceName": [
          {
            "name": "DRX-Evolution",
            "type": "model-name"
          }
        ],
        "type": {
          "text": "CR"
        },
        "version": [
          {
            "value": "5.7.412.7005"
          }
        ]
      },
      "request": {
        "method": "PUT",
        "url": "Device/5a4d77e9-04a7-4897-ad05-b80432794242"
      }
    }
  ]
}
```

## Trigger GitHub action to build and upload the library

Change `version` in `pyproject.toml` to the new version number, then run:

```shell
git add -u
git commit -m "Bump version to x.y.z"
git push origin main
git tag <version>
git push origin <version>
```

## Manually build and upload the library

Change `version` in `pyproject.toml` to the new version number, then run:

```bash
rm -rf dist/ build/ *.egg-info
python -m build
twine upload dist/*
```

## Todo 

- [x] Allow to pass custom function to create FHIR resource ids from business identifiers
- [ ] Making FHIR profiles compatible with the [MII-KDS](https://www.medizininformatik-initiative.de/en/basic-modules-mii-core-data-set)