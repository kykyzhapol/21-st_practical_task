class AirConditioning:
    '''
    Опишите класс бытовых кондиционеров воздуха AirConditioning. Опишите следующие свойства класса:
    __status
    __temperature
    Свойства должны быть защищенными, получить доступ к свойствам пользователь класса может
    вызывая методы. Опишите setter и getter методы для каждого свойства.
    Получать значения свойств пользователю класса разрешено, изменить - нет.
    Опишите следующие методы для класса:

    switch_on()
    switch_off()
    reset()
    get_temperature()
    raise_temperature()
    lower_temperature()
    При включении и перезапуске устанавливается температурный режим 18 градусов Цельсия.
    Температурный режим кондиционера от 0 до 43 градусов. Важно помнить, что управлять кондиционером
    можно только, если он включен. В выключенном состоянии, свойство __temperature  имеет значение None.
    Невозможно "до бесконечности" повышать или понижать температуру.
    Перезапускать можно только включенный кондиционер.


    '''

    def __init__(self):
        self.__status = False
        self.__temperature = None
        self.temp_distribution = [0, 43]
        self.def_temp = 18

    @property
    def status(self):
        return self.__status

    @property
    def temperature(self):
        return self.__temperature

    @status.setter
    def status(self, value):
        if isinstance(value, bool):
            self.__status = value
        else:
            print('Error - status is not bool obj')

    @temperature.setter
    def temperature(self, value):
        if 0 <= value <= 43:
            self.__temperature = value
        else:
            print('Error - out of range')

    def switch_on(self):
        self.__status = True

    def switch_off(self):
        self.__status = False


    def reset(self):
        if self.__status == True:
            self.__temperature = self.def_temp

    def get_temperature(self):
        pass

    def raise_temperature(self):
        pass

    def lower_temperature(self):
        pass