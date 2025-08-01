from dicom2fhir.dicom2fhirutils import gen_extension, add_extension_value

def create_extension(ds):

    ex_list = []

    extension_reason = gen_extension(
        url="https://www.medizininformatik-initiative.de/fhir/ext/modul-bildgebung/StructureDefinition/mii-ex-bildgebung-bildgebungsgrund")
    
    extension_r = gen_extension(url="imagingReason")

    if ds.non_empty("RequestAttributesSequence"):
        reason = ds.RequestAttributesSequence[0].get("ReasonForTheRequestedProcedure", None)
        if reason is not None:
            reason_text = str(reason.value) if hasattr(reason, "value") else str(reason)
        else: reason_text = None

        if add_extension_value(
            e = extension_r,
            url = "imagingReason",
            value= reason_text,
            system= None,
            unit= None,
            type="string"
        ):
            ex_list.append(extension_r)

    extension_reason.extension = ex_list

    if not extension_reason.extension:
        return None

    return extension_reason
