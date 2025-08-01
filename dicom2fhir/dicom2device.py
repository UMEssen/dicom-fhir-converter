import uuid
import logging
from collections.abc import Iterable
from dicom2fhir.dicom_json_proxy import DicomJsonProxy
from fhir.resources.R4B.device import Device, DeviceDeviceName
from fhir.resources.R4B.annotation import Annotation
from fhir.resources.R4B.device import DeviceUdiCarrier
from fhir.resources.R4B.meta import Meta

logger = logging.getLogger(__name__)

def _map_software_versions(ds: DicomJsonProxy) -> list[dict]:
    """
    Extract SoftwareVersions (DICOM 0018,1020) from the dataset and map to FHIR Device.version.
    
    This attribute is multi-valued (LO), so it returns a list of version strings.
    """
    # pydicom returns either a single value or a MultiValue object for VR LO
    if "SoftwareVersions" not in ds:
        return []
    
    # Normalize to list of strings
    raw = ds.SoftwareVersions
    if isinstance(raw, Iterable) and not isinstance(raw, (str, bytes)):
        return [{'value': str(item).strip()} for item in raw if item and str(item).strip()]
    else:
        cleaned = str(raw).strip()
        return [{'value': cleaned}] if cleaned else []

def build_device_resource(ds: DicomJsonProxy, config: dict) -> Device:
    """
    Build FHIR Device resource from DICOM metadata (General Equipment Module).
    Extracts manufacturer, model, serial, version, institution, station, calibration, UDI, etc.
    """

    device = Device.model_construct()
    device.meta = Meta(
        profile=["https://www.medizininformatik-initiative.de/fhir/ext/modul-bildgebung/StructureDefinition/mii-pr-bildgebung-geraet"])
    # Resource ID
    device.id = config['id_function']('Device', ds)

    # Identifiers
    identifiers = []

    if ds.non_empty("DeviceSerialNumber"):
        identifiers.append({
            "use": "official",
            "system": "urn:dicom:device-serial-number",
            "value": str(ds.DeviceSerialNumber)
        })

    if ds.non_empty("DeviceUID"):
        identifiers.append({
            "use": "official",
            "system": "urn:dicom:device-uid",
            "value": str(ds.DeviceUID)
        })

    if len(identifiers) > 0:
        device.identifier = identifiers

    # Manufacturer & Model
    if ds.non_empty("Manufacturer"):
        device.manufacturer = str(ds.Manufacturer)
    if ds.non_empty("ManufacturerModelName"):
        device.deviceName = [DeviceDeviceName.model_construct(name=str(ds.ManufacturerModelName), type="model-name")]

    # Software version(s)
    device.version = _map_software_versions(ds)

    # Institutional context
    if ds.non_empty("InstitutionName"):
        device.owner = {"display": str(ds.InstitutionName)}
    if ds.non_empty("InstitutionalDepartmentName"):
        device.location = {"display": str(ds.InstitutionalDepartmentName)}
    if ds.non_empty("StationName"):
        # set as user-friendly name according to
        # _User defined name identifying the machine..._
        device.deviceName = device.deviceName or []
        device.deviceName.append(DeviceDeviceName.model_construct(
            name=str(ds.StationName), type="user-friendly-name")
        )

    # Physical/device-specific details
    try:
        if ds.non_empty("SpatialResolution"):
            device.property = device.property or []
            device.property.append({
                "type": {"text": "spatial-resolution-mm"},
                "valueQuantity": {"value": float(ds.SpatialResolution), "unit": "mm"}
            })
    except:
        logger.warning(f"Failed to extract SpatialResolution: {ds.SpatialResolution}")

    # Calibration date/time
    dt = ""
    if ds.non_empty("DateOfLastCalibration"):
        dt += str(ds.DateOfLastCalibration) 
    if ds.non_empty("TimeOfLastCalibration"):
        dt += str(ds.TimeOfLastCalibration)
    if dt != "":
        device.note = device.note or []
        device.note.append(Annotation.model_construct(text=f"Last calibration: {dt}"))

    # Pixel padding—maybe not core but included
    if ds.non_empty("PixelPaddingValue"):
        device.note = device.note or []
        device.note.append(Annotation.model_construct(text=f"Pixel padding value: {ds.PixelPaddingValue}"))

    # UDI (Unique Device Identifier)
    if ds.non_empty("UDISequence"):
        udi_items = []
        for item in ds.UDISequence:
            if item.non_empty("UniqueDeviceIdentifier"):
                udi_items.append(DeviceUdiCarrier.model_construct(
                    deviceIdentifier=str(item.UniqueDeviceIdentifier))
                )
        if udi_items:
            device.udiCarrier = udi_items

    # Modality as device type
    if ds.non_empty("Modality"):
        device.type = {"text": str(ds.Modality)}

    return device