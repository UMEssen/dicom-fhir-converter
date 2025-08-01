# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from dateutil import tz as dateutil_tz
from fhir.resources.R4B import identifier
from fhir.resources.R4B import codeableconcept
from fhir.resources.R4B import coding
from fhir.resources.R4B import fhirtypes
from fhir.resources.R4B import reference
from fhir.resources.R4B import extension
from fhir.resources.R4B import quantity
import pandas as pd
import json
from pathlib import Path
from dicom2fhir.dicom_json_proxy import DicomJsonProxy

logger = logging.getLogger(__name__)

TERMINOLOGY_CODING_SYS = "http://terminology.hl7.org/CodeSystem/v2-0203"
TERMINOLOGY_CODING_SYS_CODE_ACCESSION = "ACSN"
TERMINOLOGY_CODING_SYS_CODE_MRN = "MR"

ACQUISITION_MODALITY_SYS = "http://dicom.nema.org/resources/ontology/DCM"
SCANNING_SEQUENCE_SYS = "https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.8.3.html"
SCANNING_VARIANT_SYS = "https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.8.3.html"

SOP_CLASS_SYS = "urn:ietf:rfc:3986"

# load rather expesive resource into global var to make it reusable
BODYSITE_SNOMED_MAPPING_PATH = Path(__file__).parent / "resources" / "terminologies" / "bodysite_snomed.json"
BODYSITE_SNOMED_MAPPING = pd.DataFrame(json.loads(BODYSITE_SNOMED_MAPPING_PATH.read_text(encoding="utf-8")))

def _get_snomed(dicom_bodypart: str, sctmapping: pd.DataFrame) -> dict[str, str] | None:
    _rec = sctmapping.loc[sctmapping['Body Part Examined'] == dicom_bodypart]
    if _rec.empty:
        return None
    return {
        'code': _rec["Code Value"].iloc[0],
        'display': _rec["Code Meaning"].iloc[0],
    }

def _coding(d: dict) -> coding.Coding | None:

    c = coding.Coding.model_construct()

    if "code" not in d:
        logger.warning(f"No code found in coding: {d}")
        return None
    if "system" in d:
        c.system = d["system"]
    else:
        logger.warning(f"No system found in coding: {d}")
    if "display" in d:
        c.display = d["display"]
    if "version" in d:
        c.display = d["version"]
    if "userSelected" in d:
        c.userSelected = d["userSelected"]
    
    return c

def gen_accession_identifier(id):
    idf = identifier.Identifier.model_construct()
    idf.use = "usual"
    idf.type = codeableconcept.CodeableConcept.model_construct()
    idf.type.coding = []
    acsn = coding.Coding.model_construct()
    acsn.system = TERMINOLOGY_CODING_SYS
    acsn.code = TERMINOLOGY_CODING_SYS_CODE_ACCESSION

    idf.type.coding.append(acsn)
    idf.value = id
    return idf

def gen_studyinstanceuid_identifier(id):
    idf = identifier.Identifier.model_construct()
    idf.system = "urn:dicom:uid"
    idf.value = "urn:oid:" + id
    return idf

def get_patient_resource_ids(PatientID, IssuerOfPatientID):
    idf = identifier.Identifier.model_construct()
    idf.use = "usual"
    idf.value = str(PatientID)

    idf.type = codeableconcept.CodeableConcept.model_construct()
    idf.type.coding = []
    id_coding = coding.Coding.model_construct()
    id_coding.system = TERMINOLOGY_CODING_SYS
    id_coding.code = TERMINOLOGY_CODING_SYS_CODE_MRN
    idf.type.coding.append(id_coding)

    if IssuerOfPatientID is not None:
        idf.assigner = reference.Reference.model_construct()
        idf.assigner.display = str(IssuerOfPatientID)

    return idf

def calc_gender(gender: str | None):
    if gender is None:
        return "unknown"
    if not gender:
        return "unknown"
    if gender.upper().lower() == "f":
        return "female"
    if gender.upper().lower() == "m":
        return "male"
    if gender.upper().lower() == "o":
        return "other"

    return "unknown"

def calc_dob(dicom_dob: str):
    if dicom_dob == '':
        return None

    try:
        dob = datetime.strptime(dicom_dob, '%Y%m%d')
        fhir_dob = fhirtypes.Date(
            dob.year,
            dob.month,
            dob.day
        )
    except Exception:
        return None
    return fhir_dob

def gen_procedurecode_array(procedures):
    if procedures is None:
        return None
    fhir_proc = []
    for p in procedures:
        concept = codeableconcept.CodeableConcept.model_construct()

        c = _coding(p)
        if c is not None:
            concept.coding = []
            concept.coding.append(c)

        if "display" in p:
            concept.text = p["display"]

        fhir_proc.append(concept)
    if len(fhir_proc) > 0:
        return fhir_proc
    return None

def gen_started_datetime(dt, tm, tz):
    """
    Generate a timezone-aware datetime object from DICOM date and time strings.

    Args:
        dt (str): DICOM date in the format 'YYYYMMDD'.
        tm (str): DICOM time in the format 'HHMMSS' or shorter.
        tz (str): Timezone as a string (e.g., 'Europe/Berlin' or '+01:00').

    Returns:
        datetime: A timezone-aware datetime object or None.
    """
    if dt is None:
        return None

    dt_pattern = '%Y%m%d'
    if tm is not None and len(tm) >= 6:
        studytm = datetime.strptime(tm[0:6], '%H%M%S')
        dt_string = f"{dt} {studytm.hour:02d}:{studytm.minute:02d}:{studytm.second:02d}"
        dt_pattern += " %H:%M:%S"
    else:
        dt_string = dt

    try:
        dt_date = datetime.strptime(dt_string, dt_pattern)
    except ValueError:
        return None

    # Apply timezone
    try:
        if tz:
            tzinfo = dateutil_tz.gettz(tz)
            if tzinfo is not None:
                dt_date = dt_date.replace(tzinfo=tzinfo)
    except Exception:
        pass

    return dt_date

def gen_reason(reason, reasonStr):
    if reason is None and reasonStr is None:
        return None
    reasonList = []
    if reason is None or len(reason) <= 0:
        # Only assign if non-empty and not just whitespace
        if reasonStr and reasonStr.strip():
            rc = codeableconcept.CodeableConcept.model_construct()
            rc.text = reasonStr
            reasonList.append(rc)
        return reasonList

    for r in reason:
        rc = codeableconcept.CodeableConcept.model_construct()
        rc.coding = []
        c = _coding(r)
        if c is not None:
            rc.coding.append(c)
        reasonList.append(rc)
    return reasonList

def gen_coding(code: str, system: str|None = None, display: str|None = None):
    if isinstance(code, list):
        raise Exception(
        "More than one code for type Coding detected")
    if not code or not code.strip():
        return None
    c = coding.Coding.model_construct()
    c.code = code
    c.system = system
    c.display = display
    if system is None and display is None:
        c.userSelected = True

    return c

def gen_codeable_concept(value_list: list, system, display=None, text=None):
    c = codeableconcept.CodeableConcept()
    c.coding = []
    for _l in value_list:
        m = gen_coding(_l, system, display)
        c.coding.append(m)
    if text is not None:
        c.text = str(text)
    return c

def gen_bodysite_coding(bd):

    bd_snomed = _get_snomed(bd, sctmapping=BODYSITE_SNOMED_MAPPING)
    
    if bd_snomed is None:
        return gen_coding(code=str(bd))
    
    return gen_coding(
        code=str(bd_snomed['code']),
        system="http://snomed.info/sct",
        display=bd_snomed['display']
    )

def dcm_coded_concept(code_sequence: list[DicomJsonProxy]):
    """    
    Convert a DICOM Code Sequence to a list of FHIR CodeableConcept objects.
    Args:
        code_sequence (list[DicomJsonProxy]): A list of DicomJsonProxy objects representing the DICOM Code Sequence.
    Returns:
        list[dict]: A list of dictionaries representing the FHIR CodeableConcept objects.
    Raises:
        TypeError: If the input is not a list of DicomJsonProxy objects.
    """

    if not isinstance(code_sequence, list):
        raise TypeError("Expected a list of DicomJsonProxy objects")

    concepts = []
    for seq in code_sequence:

        if not isinstance(seq, DicomJsonProxy):
            raise TypeError("Expected a DicomJsonProxy object in the list")

        concept = {}
        if seq.non_empty("CodeValue"):
            concept["code"] = str(seq.CodeValue)
        if seq.non_empty("CodingSchemeDesignator"):
            concept["system"] = str(seq.CodingSchemeDesignator)
        if seq.non_empty("CodeMeaning"):
            concept["display"] = str(seq.CodeMeaning)
        concepts.append(concept)
    return concepts


def gen_extension(url):
    """    
    Generates a FHIR Extension.
    Args:
        URL of the extension as string.
    Returns:
        FHIR Extension object.
    """
    e = extension.Extension()
    e.url = url
    return e


def add_extension_value(e, url, value, system, unit, type, display=None, text=None):
    """    
    Adds a single value to an existing extension.
    Args:
        e: FHIR extension object, url: URL of the nex sub-extension, value: extension value, 
        system: system of the extension value, unit: unit of the extension value, type: type of the extension value
        display and text are optional arguments.
    Returns:
        FHIR Extension object with added sub-extension.
    """

    if value is None and text is None and display is None:
        return None

    if type == "string":
        e.valueString = value
        e.url = url

    if type == "quantity":
        e.url = url
        try:
            if isinstance(value, str):
                value = value.strip()
            value = float(value)
            value_quantity = quantity.Quantity()
            value_quantity.value = value
            value_quantity.unit = unit
            value_quantity.system = system
            e.valueQuantity = value_quantity
        except (ValueError, TypeError):
            logging.warning(f"Skipping invalid Quantity.value: {value!r}. Adding as extension with valueString.")
            sub_exts = []

            ext_value = extension.Extension()
            ext_value.url = "Value.quantity.value"
            ext_value.valueString = str(value)
            sub_exts.append(ext_value)

            if unit:
                ext_unit = extension.Extension()
                ext_unit.url = "Value.quantity.unit"
                ext_unit.valueString = unit
                sub_exts.append(ext_unit)

            if system:
                ext_sys = extension.Extension()
                ext_sys.url = "Value.quantity.system"
                ext_sys.valueString = system
                sub_exts.append(ext_sys)

            e.extension = sub_exts

    if type == "boolean":
        e.url = url
        e.valueBoolean = value

    if type == "reference":
        e.url = url
        ref = reference.Reference()
        ref.reference = value
        ref.display = display
        e.valueReference = ref

    if type == "datetime":
        e.url = url
        e.valueDateTime = value

    if type == "codeableconcept":
        v = value if isinstance(value, list) else [value]
        e.url = url
        c = gen_codeable_concept(v, system, display, text)
        e.valueCodeableConcept = c

    return e