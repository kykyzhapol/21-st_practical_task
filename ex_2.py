'''
    Опишите класс корзины интернет магазина. Укажите необходимые атрибуты и методы.
    Класс должен позволять хранить данные о товарах (экземплярах класса "Товар"). Используйте
    защищенные атрибуты и методы. Хранение данных организуйте в файле. Добавьте возможность добавлять
    и удалять товар из корзины. Корзина должна иметь атрибут общей стоимости всех выбранных товаров.
    Класс "Товар" должен иметь параметр - целое число (штрих-код в стандарте EAN-13). Дополните класс атрибутами,
    таким, например как, страна производитель товара и другими, которые заполняются по штрих-коду.
    Необходимую для расшифровки штрих-кода информацию представьте в виде словаря в отдельном файле.
    Используйте set и get методы для свойств данного класса. В демонстрационном примере реализуйте
    возможность (с использованием меню) решать следующие задачи:
    1. Загружать данные о товарах из файла.
    2. Добавлять товар в корзину.
    3. Удалить товар из корзины.
    4. Посмотреть содержание корзины.
'''
import json
import os
# Глобальные данные: справочник штрих-кодов и доступный каталог товаров
barcode_info = {}          # загружается из barcode_info.json
available_barcodes = set() # загружается из файла каталога пользователем

# ----------------------------------------------------------------------
# Класс "Товар" с использованием защищённых атрибутов и property
# ----------------------------------------------------------------------
class Product:
    """Товар, идентифицируемый штрих-кодом EAN-13.
       Остальные атрибуты заполняются из глобального словаря barcode_info."""
    def __init__(self, barcode: str):
        self._barcode = None
        self._name = None
        self._country = None
        self._price = 0.0
        self._manufacturer = None
        # установка штрих-кода автоматически заполнит остальные поля
        self.barcode = barcode

    @property
    def barcode(self) -> str:
        return self._barcode

    @barcode.setter
    def barcode(self, value: str) -> None:
        """Устанавливает штрих-код (13 цифр) и загружает информацию о товаре."""
        value_str = str(value)
        if not value_str.isdigit() or len(value_str) != 13:
            raise ValueError("Штрих-код должен содержать ровно 13 цифр")
        self._barcode = value_str
        self._load_info_from_barcode()

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def country(self) -> str:
        return self._country

    @country.setter
    def country(self, value: str) -> None:
        self._country = value

    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, value: float) -> None:
        if value < 0:
            raise ValueError("Цена не может быть отрицательной")
        self._price = value

    @property
    def manufacturer(self) -> str:
        return self._manufacturer

    @manufacturer.setter
    def manufacturer(self, value: str) -> None:
        self._manufacturer = value

    def _load_info_from_barcode(self) -> None:
        """Защищённый метод: заполняет атрибуты товара из глобального barcode_info."""
        if self._barcode not in barcode_info:
            raise ValueError(f"Информация о товаре с кодом {self._barcode} не найдена")
        info = barcode_info[self._barcode]
        self._name = info.get('name', 'Неизвестно')
        self._country = info.get('country', 'Неизвестно')
        self._price = info.get('price', 0.0)
        self._manufacturer = info.get('manufacturer', 'Неизвестно')

    def __repr__(self) -> str:
        return f"Product({self._barcode}, {self._name}, {self._price} руб.)"


# ----------------------------------------------------------------------
# Класс "Корзина" с хранением данных в файле
# ----------------------------------------------------------------------
class Cart:
    """Корзина интернет-магазина. Хранит список товаров (экземпляров Product)."""
    def __init__(self, cart_file: str = "cart.json"):
        self._items = []          # список объектов Product
        self._total_price = 0.0
        self._cart_file = cart_file
        self._load()              # попытка загрузить сохранённую корзину

    @property
    def total_price(self) -> float:
        return self._total_price

    @property
    def items(self):
        """Возвращает копию списка товаров (защита от внешнего изменения)."""
        return self._items.copy()

    def _update_total(self) -> None:
        """Защищённый метод: пересчитывает общую стоимость."""
        self._total_price = sum(item.price for item in self._items)

    def add_product(self, product: Product) -> None:
        """Добавляет товар в корзину и сохраняет изменения."""
        self._items.append(product)
        self._update_total()
        self._save()

    def remove_product(self, barcode: str) -> bool:
        """Удаляет первый товар с указанным штрих-кодом. Возвращает True, если удаление выполнено."""
        barcode_str = str(barcode)
        for i, item in enumerate(self._items):
            if item.barcode == barcode_str:
                del self._items[i]
                self._update_total()
                self._save()
                return True
        return False

    def show_contents(self) -> None:
        """Выводит содержимое корзины на экран."""
        if not self._items:
            print("\nКорзина пуста.\n")
            return
        print("\nСодержимое корзины:")
        for idx, item in enumerate(self._items, 1):
            print(f"{idx}. {item.name} (код: {item.barcode})")
            print(f"   Страна: {item.country}, Производитель: {item.manufacturer}")
            print(f"   Цена: {item.price:.2f} руб.\n")
        print(f"Общая стоимость: {self._total_price:.2f} руб.\n")

    def _save(self) -> None:
        """Защищённый метод: сохраняет список штрих-кодов в файл."""
        barcodes = [item.barcode for item in self._items]
        with open(self._cart_file, 'w', encoding='utf-8') as f:
            json.dump(barcodes, f, ensure_ascii=False, indent=2)

    def _load(self) -> None:
        """Защищённый метод: загружает список штрих-кодов из файла и восстанавливает товары.
           Если barcode_info ещё не загружен, восстановление невозможно – корзина остаётся пустой."""
        if not os.path.exists(self._cart_file):
            return
        try:
            with open(self._cart_file, 'r', encoding='utf-8') as f:
                barcodes = json.load(f)
        except (json.JSONDecodeError, IOError):
            print("Ошибка чтения файла корзины. Корзина будет пустой.")
            return

        items = []
        for bc in barcodes:
            try:
                # Для создания Product требуется глобальный barcode_info
                items.append(Product(bc))
            except ValueError as e:
                print(f"Не удалось загрузить товар {bc}: {e}")
        self._items = items
        self._update_total()


# ----------------------------------------------------------------------
# Вспомогательные функции для работы с каталогом и справочником
# ----------------------------------------------------------------------
def load_barcode_info(info_file: str = "barcode_info.json") -> None:
    """Загружает справочник штрих-кодов из JSON-файла в глобальную переменную barcode_info."""
    global barcode_info
    if not os.path.exists(info_file):
        raise FileNotFoundError(f"Файл {info_file} не найден. Невозможно расшифровать штрих-коды.")
    with open(info_file, 'r', encoding='utf-8') as f:
        barcode_info = json.load(f)
    print(f"Справочник штрих-кодов загружен (записей: {len(barcode_info)}).")

def load_catalog(catalog_file: str) -> None:
    """Загружает доступные товары из файла (список штрих-кодов) в глобальную переменную available_barcodes."""
    global available_barcodes
    if not os.path.exists(catalog_file):
        print(f"Файл {catalog_file} не найден.")
        return
    with open(catalog_file, 'r', encoding='utf-8') as f:
        barcodes_list = json.load(f)
    available_barcodes = set(str(bc) for bc in barcodes_list)
    print(f"Загружено доступных товаров: {len(available_barcodes)}.")

# ----------------------------------------------------------------------
# Демонстрационное меню
# ----------------------------------------------------------------------
def main():
    # Предварительная загрузка справочника штрих-кодов (обязательно)
    try:
        load_barcode_info()
    except FileNotFoundError as e:
        print(e)
        return

    # Создаём корзину (она автоматически пытается загрузить предыдущее состояние)
    cart = Cart("cart.json")

    # Меню
    while True:
        print("\n===== МЕНЮ =====")
        print("1. Загрузить данные о товарах (каталог) из файла")
        print("2. Добавить товар в корзину")
        print("3. Удалить товар из корзины")
        print("4. Посмотреть содержимое корзины")
        print("0. Выход")
        choice = input("Ваш выбор: ").strip()

        if choice == "1":
            filename = input("Введите имя файла с каталогом (JSON-список штрих-кодов): ").strip()
            if filename:
                load_catalog(filename)
            else:
                print("Имя файла не может быть пустым.")

        elif choice == "2":
            if not available_barcodes:
                print("Сначала загрузите каталог товаров (пункт 1).")
                continue
            barcode = input("Введите штрих-код товара (13 цифр): ").strip()
            if barcode not in available_barcodes:
                print("Товар с таким штрих-кодом отсутствует в каталоге.")
                continue
            if barcode not in barcode_info:
                print("Информация о товаре не найдена в справочнике. Невозможно добавить.")
                continue
            try:
                product = Product(barcode)
                cart.add_product(product)
                print(f"Товар '{product.name}' добавлен в корзину.")
            except ValueError as e:
                print(f"Ошибка: {e}")

        elif choice == "3":
            if not cart.items:
                print("Корзина пуста, удалять нечего.")
                continue
            barcode = input("Введите штрих-код товара для удаления: ").strip()
            if cart.remove_product(barcode):
                print("Товар удалён из корзины.")
            else:
                print("Товар с таким штрих-кодом не найден в корзине.")

        elif choice == "4":
            cart.show_contents()

        elif choice == "0":
            print("До свидания!")
            break

        else:
            print("Неверный пункт меню. Попробуйте снова.")

if __name__ == "__main__":
    main()

