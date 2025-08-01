from dicom2fhir.dicom2fhirutils import gen_extension, add_extension_value


def create_extension(ds):

    ex_list = []

    extension_CT = gen_extension(
        url="https://www.medizininformatik-initiative.de/fhir/ext/modul-bildgebung/StructureDefinition/mii-ex-bildgebung-modalitaet-ct")

    # CTDIvol
    extension_CTDIvol = gen_extension(url="CTDIvol")

    if ds.non_empty("CTDIvol"):
        if add_extension_value(
            e=extension_CTDIvol,
            url="CTDIvol",
            value=ds.CTDIvol,
            system="http://unitsofmeasure.org",
            unit="milligray",
            type="quantity"
        ):
            ex_list.append(extension_CTDIvol)

    # KVP
    extension_KVP = gen_extension(url="KVP")
    if ds.non_empty("KVP"):
        if add_extension_value(
            e=extension_KVP,
            url="KVP",
            value=ds.KVP,
            system="http://unitsofmeasure.org",
            unit="kilovolt",
            type="quantity"
        ):
            ex_list.append(extension_KVP)

    # exposureTime
    extension_exposureTime = gen_extension(url="exposureTime")
    if ds.non_empty("ExposureTime"):
        if add_extension_value(
            e=extension_exposureTime,
            url="exposureTime",
            value=ds.ExposureTime,
            system="http://unitsofmeasure.org",
            unit="milliseconds",
            type="quantity"
        ):
            ex_list.append(extension_exposureTime)

    # exposure
    extension_exposure = gen_extension(url="exposure")
    if ds.non_empty("Exposure"):
        if add_extension_value(
            e=extension_exposure,
            url="exposure",
            value=ds.Exposure,
            system="http://unitsofmeasure.org",
            unit="milliampere second",
            type="quantity"
        ):
            ex_list.append(extension_exposure)

    # tube current
    extension_xRayTubeCurrent = gen_extension(url="xRayTubeCurrent")
    if ds.non_empty("XRayTubeCurrent"):
        if add_extension_value(
            e=extension_xRayTubeCurrent,
            url="xRayTubeCurrent",
            value=ds.XRayTubeCurrent,
            system="http://unitsofmeasure.org",
            unit="milliampere",
            type="quantity"
        ):
            ex_list.append(extension_xRayTubeCurrent)

    extension_CT.extension = ex_list

    if not extension_CT.extension:
        return None

    return extension_CT
