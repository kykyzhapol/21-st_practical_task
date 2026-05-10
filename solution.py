class AirConditioning:
    '''
    Класс бытовых кондиционеров воздуха.
    Управление возможно только во включенном состоянии.
    '''

    def __init__(self):
        self.__status = False          # выключен
        self.__temperature = None      # температура не определена
        self.__min_temp = 0
        self.__max_temp = 43
        self.__default_temp = 18

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, value):
        pass

    @property
    def temperature(self):
        return self.__temperature

    @temperature.setter
    def temperature(self, value):
        pass

    # Публичные методы управления
    def switch_on(self):
        """Включить кондиционер. Устанавливает температуру 18°C."""
        self.__status = True
        self.__temperature = self.__default_temp

    def switch_off(self):
        """Выключить кондиционер. Температура становится None."""
        self.__status = False
        self.__temperature = None

    def reset(self):
        """Сбросить температуру до 18°C. Работает только если кондиционер включён."""
        if self.__status:
            self.__temperature = self.__default_temp

    def get_temperature(self):
        """Вернуть текущую температуру (или None, если выключен)."""
        return self.__temperature

    def raise_temperature(self):
        """Увеличить температуру на 1°, но не выше 43°C. Работает только при включении."""
        if self.__status and self.__temperature < self.__max_temp:
            self.__temperature += 1

    def lower_temperature(self):
        """Уменьшить температуру на 1°, но не ниже 0°C. Работает только при включении."""
        if self.__status and self.__temperature > self.__min_temp:
            self.__temperature -= 1

    def __repr__(self):
        match self.__status:
            case True:
                return f"Кондиционер включен, температура = {self.__temperature}"
            case False:
                return 'Кондиционер выключен'
        return None

