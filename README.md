# dicom-fhir-converter
This project was originally forked from [alexa-ian/dicom-fhir-converter](https://github.com/alexa-ian/dicom-fhir-converter). However, due to extensive refactoring and structural changes, it has since been detached from the upstream repository and is now maintained as an independent, standalone Python library.

The library converts DICOM data into a FHIR transaction Bundle that includes an ImagingStudy resource, a Patient resource, a Device resource, and optionally Observation resources. It supports two input modes: either a directory containing DICOM files (recursively parsed), or an `Iterable` of `pydicom.Dataset` instances passed directly to the API.

This library utilizes the following projects:
- fhir.resources project (https://pypi.org/project/fhir.resources/) - used to create FHIR models
- pydicom (https://pydicom.github.io/) - used to read dicom instances

The library does not rely on the terminology service therefore, any coding that requires a look-up were coded with ```"userSelected=True"``` values.

## Usage

```python
from dicom2fhir.dicom2fhir import process_dicom_2_fhir
from pprint import pprint

# Process a directory of DICOM files
bundle = process_dicom_2_fhir("study directory")

# Or provide an iterable of pydicom.Dataset objects directly
# datasets = [pydicom.dcmread(path) for path in file_paths]
# bundle = process_dicom_2_fhir(datasets)

# Print the resulting FHIR Bundle as JSON
pprint(bundle.model_dump_json(indent=2))
```

The resulting object is a FHIR transaction Bundle containing:
-	One ImagingStudy resource
-	One Patient resource
-	One Device resource
-	Optionally, one or more Observation resources

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

## Build and upload the library

```bash
rm -rf dist/ build/ *.egg-info
python -m build
twine upload dist/*
```

## Todo 

- [x] Allow to pass custom function to create FHIR resource ids from business identifiers
- [ ] Add support for DICOMweb data inputs