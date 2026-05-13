"""
Module containing a class for household air conditioners.

The class provides control methods that only work when the device is switched on.
"""


class AirConditioning:
    """
    A household air conditioner.

    Only methods that change the temperature or reset it work when the
    device is turned on (status = True). The temperature range is 0°C to 43°C,
    with a default of 18°C when switched on.
    """

    def __init__(self) -> None:
        """Initialise the air conditioner as switched off with no temperature."""
        self.__status: bool = False          # False = off, True = on
        self.__temperature: int | None = None      # current temperature (None if off)
        self.__min_temp: int = 0
        self.__max_temp: int = 43
        self.__default_temp: int = 18

    # --- Properties (getters / setters) ---------------------------------------

    @property
    def status(self) -> bool:
        """Return the current power status (True = on, False = off)."""
        return self.__status

    @status.setter
    def status(self, value: bool) -> None:
        """Setter for status (intentionally does nothing, use switch_on/off)."""
        pass   # functional part unchanged: setter does nothing

    @property
    def temperature(self) -> int | None:
        """Return the current temperature or None if the device is off."""
        return self.__temperature

    @temperature.setter
    def temperature(self, value: int) -> None:
        """Setter for temperature (intentionally does nothing, use raise/lower)."""
        pass   # functional part unchanged

    # --- Public control methods -----------------------------------------------

    def switch_on(self) -> None:
        """
        Turn the air conditioner on.

        Sets the temperature to the default value (18°C).
        """
        self.__status = True
        self.__temperature = self.__default_temp

    def switch_off(self) -> None:
        """Turn the air conditioner off and reset the temperature to None."""
        self.__status = False
        self.__temperature = None

    def reset(self) -> None:
        """
        Reset the temperature to the default (18°C).

        Only works when the device is switched on.
        """
        if self.__status:
            self.__temperature = self.__default_temp

    def get_temperature(self) -> int | None:
        """
        Return the current temperature.

        Returns:
            int | None: The current temperature if the device is on,
                        otherwise None.
        """
        return self.__temperature

    def raise_temperature(self) -> None:
        """
        Increase the temperature by 1°C (max 43°C).

        Only works when the device is switched on.
        """
        if self.__status and self.__temperature < self.__max_temp:
            self.__temperature += 1

    def lower_temperature(self) -> None:
        """
        Decrease the temperature by 1°C (min 0°C).

        Only works when the device is switched on.
        """
        if self.__status and self.__temperature > self.__min_temp:
            self.__temperature -= 1

    # --- Special methods ------------------------------------------------------

    def __repr__(self) -> str:
        """
        Return a string representation of the air conditioner.

        Returns:
            str: A description of the current state (on/off and temperature).
        """
        if self.__status:
            return f"Air conditioner is on, temperature = {self.__temperature}"
        else:
            return "Air conditioner is off"
