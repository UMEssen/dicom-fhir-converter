import json
import pandas as pd
from pathlib import Path
from dicom2fhir.dicom2fhirutils import gen_extension, add_extension_value

RADIONUCLIDE_MAPPING_PATH = Path(
    __file__).parent.parent / "resources" / "terminologies" / "radionuclide_PT.json"
RADIONUCLIDE_MAPPING = pd.DataFrame(json.loads(
    RADIONUCLIDE_MAPPING_PATH.read_text(encoding="utf-8")))
RADIOPHARMACEUTICAL_MAPPING_PATH = Path(
    __file__).parent.parent / "resources" / "terminologies" / "radiopharmaceutical_PT.json"
RADIOPHARMACEUTICAL_MAPPING = pd.DataFrame(json.loads(
    RADIONUCLIDE_MAPPING_PATH.read_text(encoding="utf-8")))
UNITS_CSV_PATH = Path(__file__).parent.parent / \
    "resources" / "terminologies" / "units.csv"
UNITS_MAPPING = pd.read_csv(UNITS_CSV_PATH, encoding="utf-8")
EXTENSION_PT_URL = "https://www.medizininformatik-initiative.de/fhir/ext/modul-bildgebung/StructureDefinition/mii-ex-bildgebung-modalitaet-pt"

def parse_time_to_seconds(time_str):
    hours = int(time_str[:2])  # Hours
    minutes = int(time_str[2:4])  # Minutes
    seconds = float(time_str[4:])  # Seconds + Milliseconds

    return hours * 3600 + minutes * 60 + seconds


def _get_snomed(value, sctmapping):

    # Check: 'SNOMED-RT ID'
    match = sctmapping[sctmapping['SNOMED-RT ID'] == value]
    if not match.empty:
        row = match.iloc[0]
        return row["Code Value"], row["Code Meaning"]

    # Check: 'Code Meaning'
    match = sctmapping[sctmapping['Code Meaning'] == value]
    if not match.empty:
        row = match.iloc[0]
        return row["Code Value"], row["Code Meaning"]

    # Check: already valid 'Code Value'
    match = sctmapping[sctmapping['Code Value'] == value]
    if not match.empty:
        row = match.iloc[0]
        return row["Code Value"], row["Code Meaning"]

    # No mapping found
    return None, None


def get_units_mapping(csv_mapping, value):

    # Check DICOM value
    match = csv_mapping[csv_mapping['DICOM Value'] == value]
    if not match.empty:
        row = match.iloc[0]
        return row.iloc[1], row.iloc[2]

    # Check Value itself
    match = csv_mapping[csv_mapping['Code Value'] == value]
    if not match.empty:
        row = match.iloc[0]
        return row.iloc[1], row.iloc[2]
    # No mapping found
    return None, None


def create_extension(ds):

    ex_list = []

    extension_PT = gen_extension(url=EXTENSION_PT_URL)

    # units
    extension_units = gen_extension(url="units")

    if ds.non_empty("Units"):
        units_value, units_display = get_units_mapping(UNITS_MAPPING, ds.Units)
        if add_extension_value(
            e=extension_units,
            url="units",
            value=units_value,
            system="http://unitsofmeasure.org",
            display=units_display,
            unit=None,
            type="codeableconcept"
        ):
            ex_list.append(extension_units)

    # Tracer Einwirkzeit
    extension_tracerExposureTime = gen_extension(url="tracerExposureTime")
    if ds.non_empty("RadiopharmaceuticalInformationSequence") and ds.non_empty("AcquisitionTime"):
        try:
            acq_time = parse_time_to_seconds(str(ds.AcquisitionTime))
            start_time = parse_time_to_seconds(
                str(ds.RadiopharmaceuticalInformationSequence[0].RadiopharmaceuticalStartTime))
            diff_time = abs(acq_time - start_time)
        except Exception as e:
            print(f"Could not calculate the Exposure Time: {e}")
            diff_time = None
            pass

        if add_extension_value(
            e=extension_tracerExposureTime,
            url="tracerExposureTime",
            value=diff_time,
            system="http://unitsofmeasure.org",
            unit="seconds",
            type="quantity"
        ):
            ex_list.append(extension_tracerExposureTime)

    # Radiopharmakon
    extension_radiopharmaceutical = gen_extension(url="radiopharmaceutical")
    if ds.non_empty("RadiopharmaceuticalInformationSequence"):
        snomed_value, snomed_display = _get_snomed(
            ds.RadiopharmaceuticalInformationSequence[0].Radiopharmaceutical, sctmapping=RADIOPHARMACEUTICAL_MAPPING)
        if add_extension_value(
            e=extension_radiopharmaceutical,
            url="radiopharmaceutical",
            value=snomed_value,
            system="http://snomed.info/sct",
            display=snomed_display,
            unit=None,
            text=ds.RadiopharmaceuticalInformationSequence[0].Radiopharmaceutical,
            type="codeableconcept"
        ):
            ex_list.append(extension_radiopharmaceutical)

    # radionuclideTotalDose
    extension_radionuclideTotalDose = gen_extension(
        url="radionuclideTotalDose")
    if ds.non_empty("RadiopharmaceuticalInformationSequence"):
        if add_extension_value(
            e=extension_radionuclideTotalDose,
            url="radionuclideTotalDose",
            value=ds.RadiopharmaceuticalInformationSequence[0].RadionuclideTotalDose,
            system="http://unitsofmeasure.org",
            unit="Megabecquerel",
            type="quantity"
        ):
            ex_list.append(extension_radionuclideTotalDose)

    # radionuclideHalfLife
    extension_radionuclideHalfLife = gen_extension(url="radionuclideHalfLife")
    if ds.non_empty("RadiopharmaceuticalInformationSequence[0].RadionuclideHalfLife"):
        if add_extension_value(
            e=extension_radionuclideHalfLife,
            url="radionuclideHalfLife",
            value=ds.RadiopharmaceuticalInformationSequence[0].RadionuclideHalfLife,
            system="http://unitsofmeasure.org",
            unit="Seconds",
            type="quantity"
        ):
            ex_list.append(extension_radionuclideHalfLife)

    # Radionuklid
    extension_radionuclide = gen_extension(url="radionuclide")

    if ds.non_empty("RadiopharmaceuticalInformationSequence"):
        snomed_value, snomed_display = _get_snomed(
            ds.RadiopharmaceuticalInformationSequence[0].RadionuclideCodeSequence[0].CodeValue, sctmapping=RADIONUCLIDE_MAPPING)
        if add_extension_value(
            e=extension_radionuclide,
            url="radionuclide",
            value=snomed_value,
            system="http://snomed.info/sct",
            display=snomed_display,
            unit=None,
            text=ds.RadiopharmaceuticalInformationSequence[0].RadionuclideCodeSequence[0].CodeValue,
            type="codeableconcept"
        ):
            ex_list.append(extension_radionuclide)

    # Series type
    extension_seriesType = gen_extension(url="seriesType")
    if ds.non_empty("SeriesType"):
        if add_extension_value(
            e=extension_seriesType,
            url="seriesType",
            value=ds.get_list("SeriesType"),
            system="https://www.medizininformatik-initiative.de/fhir/ext/modul-bildgebung/CodeSystem/mii-cs-bildgebung-series-type",
            unit=None,
            type="codeableconcept"
        ):
            ex_list.append(extension_seriesType)

    extension_PT.extension = ex_list

    if not extension_PT.extension:
        return None

    return extension_PT
