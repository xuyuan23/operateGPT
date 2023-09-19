from dataclasses import dataclass, fields
from typing import Optional, Type


@dataclass
class BaseParameters:
    @classmethod
    def from_dict(
        cls, data: dict, ignore_extra_fields: bool = False
    ) -> "BaseParameters":
        """Create an instance of the dataclass from a dictionary.

        Args:
            data: A dictionary containing values for the dataclass fields.
            ignore_extra_fields: If True, any extra fields in the data dictionary that are
                not part of the dataclass will be ignored.
                If False, extra fields will raise an error. Defaults to False.
        Returns:
            An instance of the dataclass with values populated from the given dictionary.

        Raises:
            TypeError: If `ignore_extra_fields` is False and there are fields in the
                           dictionary that aren't present in the dataclass.
        """
        all_field_names = {f.name for f in fields(cls)}
        if ignore_extra_fields:
            data = {key: value for key, value in data.items() if key in all_field_names}
        else:
            extra_fields = set(data.keys()) - all_field_names
            if extra_fields:
                raise TypeError(f"Unexpected fields: {', '.join(extra_fields)}")
        return cls(**data)

    def __str__(self) -> str:
        class_name = self.__class__.__name__
        parameters = [
            f"\n\n=========================== {class_name} ===========================\n"
        ]
        for field_info in fields(self):
            value = _get_simple_privacy_field_value(self, field_info)
            parameters.append(f"{field_info.name}: {value}")
        parameters.append(
            "\n======================================================================\n\n"
        )
        return "\n".join(parameters)


def _get_simple_privacy_field_value(obj, field_info):
    """Retrieve the value of a field from a dataclass instance, applying privacy rules if necessary.

    This function reads the metadata of a field to check if it's tagged with 'privacy'.
    If the 'privacy' tag is present, then it modifies the value based on its type
    for privacy concerns:
    - int: returns -999
    - float: returns -999.0
    - bool: returns False
    - str: if length > 5, masks the middle part and returns first and last char;
           otherwise, returns "******"

    Args:
        obj: The dataclass instance.
        field_info: A Field object that contains information about the dataclass field.

    Returns:
    The original or modified value of the field based on the privacy rules.

    Example usage:
    @dataclass
    class Person:
        name: str
        age: int
        ssn: str = field(metadata={"tags": "privacy"})
    p = Person("Alice", 30, "123-45-6789")
    print(_get_simple_privacy_field_value(p, Person.ssn))  # A******9
    """
    tags = field_info.metadata.get("tags")
    tags = [] if not tags else tags.split(",")
    is_privacy = False
    if tags and "privacy" in tags:
        is_privacy = True
    value = getattr(obj, field_info.name)
    if not is_privacy or not value:
        return value
    field_type = EnvArgumentParser.get_argparse_type(field_info.type)
    if field_type is int:
        return -999
    if field_type is float:
        return -999.0
    if field_type is bool:
        return False
    # str
    if len(value) > 5:
        return value[0] + "******" + value[-1]
    return "******"


class EnvArgumentParser:
    @staticmethod
    def get_env_prefix(env_key: str) -> str:
        if not env_key:
            return None
        env_key = env_key.replace("-", "_")
        return env_key + "_"

    @staticmethod
    def get_argparse_type(field_type: Type) -> Type:
        # Return the appropriate type for argparse to use based on the field type
        if field_type is int or field_type == Optional[int]:
            return int
        elif field_type is float or field_type == Optional[float]:
            return float
        elif field_type is bool or field_type == Optional[bool]:
            return bool
        elif field_type is str or field_type == Optional[str]:
            return str
        else:
            raise ValueError(f"Unsupported parameter type {field_type}")
