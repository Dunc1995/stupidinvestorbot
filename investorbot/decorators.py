import logging

from requests import HTTPError

from investorbot.constants import DEFAULT_LOGS_NAME


logger = logging.getLogger(DEFAULT_LOGS_NAME)


def no_scientific_notation(func: callable):
    """Forces Python to print raw float values without scientific notation and without floating
    point errors."""

    def wrapper(self) -> str:
        value = func(self)

        if not isinstance(value, float) and not isinstance(value, int):
            raise TypeError(
                f"no_scientific_notation decorator was assigned to a method return type ({type(value)})"
                + "when it expects either a float or integer type."
            )

        result = format(value).lower()

        # Python has made me resort to this if statement to get rid of scientific notation
        if "e" in result:
            # e.g. 1.05e5 - decimal_value = 1.05 and exponent_value = 5
            decimal_value = float(result.split("e")[0])
            exponent_value = int(result.split("e")[1])

            # Ensure decimal_value is positive.
            decimal_value = -1 * decimal_value if decimal_value < 0 else decimal_value

            decimal_value_string_init = str(decimal_value)

            # If a decimal point exists, strip trailing zeros.
            decimal_value_string = (
                decimal_value_string_init.rstrip("0").replace(".", "")
                if "." in decimal_value_string_init
                else decimal_value_string_init
            )
            precision = len(decimal_value_string) - 1

            # Ensure exponent_value is positive.
            exponent_value = (
                -1 * exponent_value if exponent_value < 0 else exponent_value
            )

            result = format(value, f".{exponent_value + precision}f")

        return result

    return wrapper


def routine(name="Unnamed Routine"):
    """Prepends and appends log messages to signal the start and end of a given routine. This is
    useful when multiple routines are being triggered concurrently."""

    def routine_internal(func):
        def wrapper(**kwargs):
            printed_name = name.upper()
            logger.info(f">>>---START {printed_name} ROUTINE---<<<")
            try:
                func(**kwargs)
            except HTTPError as http_error:
                logger.fatal(http_error)

                if http_error.response.status_code == 401:
                    logger.info(
                        "Your IP address likely needs to be whitelisted on your API security settings,"
                        + " assuming your API keys are set correctly with necessary permissions."
                    )
            logger.info(f">>>---END {printed_name} ROUTINE---<<<")

        _wrapper = wrapper
        _wrapper.__name__ = func.__name__  # Ensures unique function name
        _wrapper.__doc__ = func.__doc__  # Exposes docstring to argh

        return _wrapper

    return routine_internal
