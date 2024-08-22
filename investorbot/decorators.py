import logging

from investorbot.constants import DEFAULT_LOGS_NAME


logger = logging.getLogger(DEFAULT_LOGS_NAME)


def no_scientific_notation(func: callable):
    def wrapper(self) -> str:
        value = func(self)

        if not isinstance(value, float) and not isinstance(value, int):
            raise TypeError(
                f"no_scientific_notation decorator was assigned to a method return type ({type(value)})"
                + "when it expects either a float or integer type."
            )

        result = format(value).lower()

        #! Python has made me resort to this if statement to get rid of bloody
        #! scientific notation
        if "e" in result:
            decimal_value = float(result.split("e")[0])
            exponent_value = int(result.split("e")[1])

            decimal_value = -1 * decimal_value if decimal_value < 0 else decimal_value

            decimal_value_string_init = str(decimal_value)

            decimal_value_string = (
                decimal_value_string_init.rstrip("0").replace(".", "")
                if "." in decimal_value_string_init
                else decimal_value_string_init
            )
            precision = len(decimal_value_string) - 1

            exponent_value = (
                -1 * exponent_value if exponent_value < 0 else exponent_value
            )

            result = format(value, f".{exponent_value + precision}f")

        return result

    return wrapper


def format_float(precision: None | int = None):
    def format_float_internal(func: callable):
        def wrapper(self) -> str:
            value = func(self)

            if not isinstance(value, float) and not isinstance(value, int):
                raise TypeError(
                    f"formatted_numeric decorator was assigned to a method return type ({type(value)})"
                    + "when it expects either a float or integer type."
                )

            result = format(value, f".{precision}f")

            return result

        return wrapper

    return format_float_internal


def routine(name="Unnamed Routine"):
    def routine_internal(func):
        def wrapper():
            printed_name = name.upper()

            logger.info(f">>>---START {printed_name} ROUTINE---<<<")
            func()
            logger.info(f">>>---END {printed_name} ROUTINE---<<<")

        _wrapper = wrapper
        _wrapper.__name__ = func.__name__  # Ensures unique function name
        _wrapper.__doc__ = func.__doc__  # Exposes docstring to argh

        return _wrapper

    return routine_internal
