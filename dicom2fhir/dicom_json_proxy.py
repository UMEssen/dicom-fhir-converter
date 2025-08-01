import json
from pydicom.datadict import tag_for_keyword
from pydicom.tag import Tag

class DicomJsonProxy:
    def __init__(self, dicom_json: dict):
        self._raw = dicom_json

    def __repr__(self):
        return json.dumps(self._raw, indent=2)

    def __str__(self):
        return repr(self)

    def __getattr__(self, tag_name):
        tag = tag_for_keyword(tag_name)
        if tag is None:
            raise AttributeError(f"Unknown DICOM keyword: {tag_name}")
        key = f"{tag >> 16:04X}{tag & 0xFFFF:04X}"
        try:
            return self._extract_value(self._raw[key])
        except KeyError:
            raise AttributeError(f"No such DICOM attribute: {tag_name}")

    def __getitem__(self, tag):
        if tag in self._raw:
            return self._extract_value(self._raw[tag])
        raise KeyError(f"Tag {tag} not found in DICOM JSON.")

    def __contains__(self, tag_or_keyword):
        # Handle keyword like "PatientID"
        if isinstance(tag_or_keyword, str):
            tag = tag_for_keyword(tag_or_keyword)
            if tag is None:
                return False
            tag_key = f"{tag >> 16:04X}{tag & 0xFFFF:04X}"
        # Handle int or Tag
        elif isinstance(tag_or_keyword, (int, Tag)):
            tag = Tag(tag_or_keyword)
            tag_key = f"{tag.group:04X}{tag.element:04X}"
        else:
            return False
        return tag_key in self._raw

    def _extract_value(self, elem):

        def _wrap_as_proxy(value):
            if isinstance(value, dict):
                return DicomJsonProxy(value)
            elif isinstance(value, list):
                return [DicomJsonProxy(item) if isinstance(item, dict) else item for item in value]
            return value

        if isinstance(elem, dict) and "Value" in elem and "vr" in elem:
            if elem["vr"] == "SQ":
                return _wrap_as_proxy(elem["Value"]) or []
            return _wrap_as_proxy(elem["Value"][0]) if isinstance(elem["Value"], list) else _wrap_as_proxy(elem["Value"])
        return _wrap_as_proxy(elem)

    def get(self, name, default=None):
        try:
            return getattr(self, name)
        except AttributeError:
            return default
        
    def non_empty(self, name):
        """
        Check if the DICOM attribute is present and not empty.
        """
        value = self.get(name)

        # Handle cases where value is a dict or list
        if isinstance(value, dict) or isinstance(value, DicomJsonProxy):
            if "Value" in value:
                value = value["Value"]
            else:
                return False
        if isinstance(value, list):
            return len(value) > 0

        return value is not None and str(value).strip() != ''

    def get_list(self, name):
        """
        Returns all values of a DICOM element, even for multi-value attributes.
        """
        tag = tag_for_keyword(name)
        if tag is None:
            raise AttributeError(f"Unknown DICOM keyword: {name}")
        key = f"{tag >> 16:04X}{tag & 0xFFFF:04X}"
        elem = self._raw.get(key)

        if not elem or "Value" not in elem:
            return []

        value = elem["Value"]
        if elem["vr"] == "SQ":
            return [DicomJsonProxy(item) for item in value]
        return value