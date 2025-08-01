from dicom2fhir.dicom2fhirutils import gen_extension, add_extension_value

EXTENSION_MR_URL = "https://www.medizininformatik-initiative.de/fhir/ext/modul-bildgebung/StructureDefinition/mii-ex-bildgebung-modalitaet-mr"


def create_extension(ds):

    ex_list = []

    extension_MR = gen_extension(
        url=EXTENSION_MR_URL)

    # scanning sequence
    extension_scanningSequence = gen_extension(url="scanningSequence")

    if ds.non_empty("ScanningSequence"):
        value = ds.ScanningSequence
        # needs testing! only tested with data from UKER
        sequence_values = value.split("\\")

        if add_extension_value(
            e=extension_scanningSequence,
            url="scanningSequence",
            value=sequence_values,
            system="https://www.medizininformatik-initiative.de/fhir/ext/modul-bildgebung/CodeSystem/mii-cs-bildgebung-scanning-sequence",
            unit=None,
            type="codeableconcept",
        ):
            ex_list.append(extension_scanningSequence)

    # scanning sequence variant
    extension_scanningSequenceVariant = gen_extension(
        url="scanningSequenceVariant")

    if ds.non_empty("SequenceVariant"):

        if add_extension_value(
            e=extension_scanningSequenceVariant,
            url="scanningSequenceVariant",
            value=ds.get_list("SequenceVariant"),
            system="https://www.medizininformatik-initiative.de/fhir/ext/modul-bildgebung/CodeSystem/mii-cs-bildgebung-scanning-sequence-variant",
            unit=None,
            type="codeableconcept"
        ):
            ex_list.append(extension_scanningSequenceVariant)

    # feldstärke
    extension_magneticFieldStrength = gen_extension(
        url="magneticFieldStrength")

    if ds.non_empty("MagneticFieldStrength"):
        if add_extension_value(
            e=extension_magneticFieldStrength,
            url="magneticFieldStrength",
            value=ds.MagneticFieldStrength,
            system="http://unitsofmeasure.org",
            unit="tesla",
            type="quantity"
        ):
            ex_list.append(extension_magneticFieldStrength)

    # TE
    extension_TE = gen_extension(url="echoTime")

    if ds.non_empty("EchoTime"):
        if add_extension_value(
            e=extension_TE,
            url="echoTime",
            value=ds.EchoTime,
            system="http://unitsofmeasure.org",
            unit="milliseconds",
            type="quantity"
        ):
            ex_list.append(extension_TE)

    # TR
    extension_TR = gen_extension(url="repetitionTime")

    if ds.non_empty("RepetitionTime"):
        if add_extension_value(
            e=extension_TR,
            url="repetitionTime",
            value=ds.RepetitionTime,
            system="http://unitsofmeasure.org",
            unit="milliseconds",
            type="quantity"
        ):
            ex_list.append(extension_TR)

    # TI
    extension_TI = gen_extension(url="inversionTime")

    if ds.non_empty("InversionTime"):
        if add_extension_value(
            e=extension_TI,
            url="inversionTime",
            value=ds.InversionTime,
            system="http://unitsofmeasure.org",
            unit="milliseconds",
            type="quantity"
        ):
            ex_list.append(extension_TI)

    # kippwinkel
    extension_flipAngle = gen_extension(url="flipAngle")

    if ds.non_empty("FlipAngle"):
        if add_extension_value(
            e=extension_flipAngle,
            url="flipAngle",
            value=ds.FlipAngle,
            system="http://unitsofmeasure.org",
            unit="plane angle degree",
            type="quantity"
        ):
            ex_list.append(extension_flipAngle)

    extension_MR.extension = ex_list

    if not extension_MR.extension:
        return None

    return extension_MR
