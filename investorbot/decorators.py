import logging

from investorbot.constants import DEFAULT_LOGS_NAME


logger = logging.getLogger(DEFAULT_LOGS_NAME)


def __format(value: float):
    return f"{value:g}"


def formatted_numeric(func: callable):
    def wrapper(self) -> str:
        result = func(self)

        if not isinstance(result, float):
            raise TypeError(
                f"formatted_numeric decorator was assigned to a method return type ({type(result)})"
                + "when it expects either a float or integer type."
            )

        return __format(result)

    return wrapper


def routine(name="Unnamed Routine"):
    def routine_internal(func: callable):
        def wrapper():
            printed_name = name.upper()

            logger.info(f">>>---START {printed_name} ROUTINE---<<<")
            func()
            logger.info(f">>>---END {printed_name} ROUTINE---<<<")

        return wrapper

    return routine_internal
