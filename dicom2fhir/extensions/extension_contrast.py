from dicom2fhir.dicom2fhirutils import gen_extension, add_extension_value

def create_extension(ds):

    ex_list = []

    extension_contrast = gen_extension(url="https://www.medizininformatik-initiative.de/fhir/ext/modul-bildgebung/StructureDefinition/mii-ex-bildgebung-kontrastmittel")

    #contrastBolus
    extension_contrastBolus = gen_extension(url="contrastBolus")
    if ds.non_empty("ContrastBolusAgent"):
        valueContrast = True
    else:
        valueContrast = False

    if add_extension_value(
        e = extension_contrastBolus,
        url = "contrastBolus",
        value=valueContrast,
        system=None,
        unit= None,
        type="boolean"
    ):
        ex_list.append(extension_contrastBolus)
    
    #contrastBolusDetails
    if ds.non_empty("ContrastBolusAgent"):
        display_value = ds.ContrastBolusAgent
        extension_contrastBolusDetails = gen_extension(url="contrastBolusDetails")
        if add_extension_value(
            e = extension_contrastBolusDetails,
            url = "contrastBolusDetails",
            value= None,
            system=None,
            unit= None,
            display=display_value,
            type="reference"
        ):
            ex_list.append(extension_contrastBolusDetails)
    
    extension_contrast.extension = ex_list

    if not extension_contrast.extension:
        return None

    return extension_contrast
