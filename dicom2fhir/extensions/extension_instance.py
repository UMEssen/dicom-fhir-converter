from dicom2fhir.dicom2fhirutils import gen_extension, add_extension_value

EXTENSION_INSTANCE_URL = "https://www.medizininformatik-initiative.de/fhir/ext/modul-bildgebung/StructureDefinition/mii-ex-bildgebung-instanz-details"


def create_extension(ds):

    ex_list = []

    extension_instance = gen_extension(url=EXTENSION_INSTANCE_URL)
    if ds.non_empty("PixelSpacing"):
        pixelspacings = ds.get_list("PixelSpacing")
        pixelSpacingX = pixelspacings[0]
        pixelSpacingY = pixelspacings[1]

        # pixelSpacing(x)
        extension_pixelSpacingX = gen_extension(url="pixelSpacing(x)")
        if add_extension_value(
            e=extension_pixelSpacingX,
            url="pixelSpacingX",
            value=pixelSpacingX,
            system="http://unitsofmeasure.org",
            unit="millimeter",
            type="quantity"
        ):
            ex_list.append(extension_pixelSpacingX)

        # pixelSpacing(y)
        extension_pixelSpacingY = gen_extension(
            url="pixelSpacing(y)"
        )
        if add_extension_value(
            e=extension_pixelSpacingY,
            url="pixelSpacingY",
            value=pixelSpacingY,
            system="http://unitsofmeasure.org",
            unit="millimeter",
            type="quantity"
        ):
            ex_list.append(extension_pixelSpacingY)

    # sliceThickness
    if ds.non_empty("SliceThickness"):
        extension_sliceThickness = gen_extension(url="sliceThickness")
        if add_extension_value(
            e=extension_sliceThickness,
            url="sliceThickness",
            value=ds.SliceThickness,
            system="http://unitsofmeasure.org",
            unit="millimeter",
            type="quantity"
        ):
            ex_list.append(extension_sliceThickness)

    # imageType
    extension_imageType = gen_extension(url="imageType")
    if ds.non_empty("ImageType"):

        if add_extension_value(
            e=extension_imageType,
            url="imageType",
            value=ds.get_list("ImageType"),
            system="https://www.medizininformatik-initiative.de/fhir/ext/modul-bildgebung/CodeSystem/mii-cs-bildgebung-instance-image-type",
            unit=None,
            type="codeableconcept"
        ):
            ex_list.append(extension_imageType)

    extension_instance.extension = ex_list

    if not extension_instance.extension:
        return None

    return extension_instance
