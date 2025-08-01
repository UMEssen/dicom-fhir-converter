# -*- coding: utf-8 -*-
import logging
from typing import List
from fhir.resources.R4B.observation import Observation
from fhir.resources.R4B.patient import Patient
from fhir.resources.R4B.imagingstudy import ImagingStudy
from fhir.resources.R4B.quantity import Quantity
from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.coding import Coding
from fhir.resources.R4B.reference import Reference
from fhir.resources.R4B.meta import Meta
from dicom2fhir.dicom2fhirutils import gen_started_datetime
from dicom2fhir.dicom_json_proxy import DicomJsonProxy

logger = logging.getLogger(__name__)

def build_observation_resources(ds: DicomJsonProxy, patient: Patient, study: ImagingStudy, config: dict) -> List[Observation]:
    observations = []
    
    def create_obs(code: str, display: str, value: float, unit: str, system: str, code_unit: str) -> Observation:
        return Observation.model_construct(
            id=config['id_function']('Observation', ds, extra=code),
            meta = Meta(profile=["https://www.medizininformatik-initiative.de/fhir/ext/modul-bildgebung/StructureDefinition/mii-pr-bildgebung-radiologische-beobachtung"]),
            status="final",
            category=[CodeableConcept.model_construct(
                coding=[Coding.model_construct(system="http://terminology.hl7.org/CodeSystem/observation-category", code="vital-signs")]
            )],
            code=CodeableConcept.model_construct(
                coding=[Coding.model_construct(system="http://loinc.org", code=code, display=display)],
                text=display
            ),
            subject=Reference.model_construct(reference=f"Patient/{patient.id}") if patient else None,
            partOf=[Reference.model_construct(reference=f"ImagingStudy/{study.id}")] if study else [],
            effectiveDateTime=gen_started_datetime(ds.StudyDate, ds.StudyTime, config["dicom_timezone"]),
            valueQuantity=Quantity.model_construct(value=value, unit=unit, system=system, code=code_unit)
        )

    if "PatientWeight" in ds and ds.PatientWeight is not None:
        try:
            weight = float(ds.PatientWeight)
            observations.append(create_obs("29463-7", "Body Weight", weight, "kg", "http://unitsofmeasure.org", "kg"))
        except:
            logger.warning(f"Failed to extract PatientWeight: {ds.PatientWeight}")

    if "PatientSize" in ds and ds.PatientSize is not None:
        try:
            height = float(ds.PatientSize)
            observations.append(create_obs("8302-2", "Body Height", height, "m", "http://unitsofmeasure.org", "m"))
        except:
            logger.warning(f"Failed to extract PatientSize: {ds.PatientSize}")

    return observations