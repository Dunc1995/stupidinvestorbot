import datetime


def format_numeric(precision: None | int = None):
    def format_numeric_internal(func: callable):
        def wrapper(self) -> str:
            value = func(self)

            if not isinstance(value, float) and not isinstance(value, int):
                raise TypeError(
                    f"format_numeric decorator was assigned to a method return type ({type(value)})"
                    + "when it expects either a float or integer type."
                )

            result = format(value, f".{precision}f")

            return result

        return wrapper

    return format_numeric_internal


def format_date(func: callable):
    def wrapper(self) -> str:
        date_object: datetime.datetime = func(self)

        result = date_object.strftime("%b %d %Y %H:%M:%S")

        return result

    return wrapper
