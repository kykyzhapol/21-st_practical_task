"""
Shopping cart system for an online store.

Provides classes for products (identified by EAN-13 barcodes) and a shopping cart
that stores products, calculates total price, and persists data to JSON files.
"""

import json
import os

# Global data: barcode reference (loaded from barcode_info.json) and available product catalog
barcode_info = {}           # Loaded from barcode_info.json
available_barcodes = set()  # Loaded from a catalog file chosen by the user


# ----------------------------------------------------------------------
# Product class with protected attributes and property getters/setters
# ----------------------------------------------------------------------
class Product:
    """
    A product identified by an EAN-13 barcode.

    Other attributes (name, country, price, manufacturer) are loaded
    from the global barcode_info dictionary.
    """

    def __init__(self, barcode: str):
        """
        Initialise a product with a barcode.

        Args:
            barcode: 13‑digit string representing the EAN‑13 code.
        """
        self._barcode = None
        self._name = None
        self._country = None
        self._price = 0.0
        self._manufacturer = None
        # Setting the barcode automatically loads the remaining fields
        self.barcode = barcode

    @property
    def barcode(self) -> str:
        """Return the product's barcode."""
        return self._barcode

    @barcode.setter
    def barcode(self, value: str) -> None:
        """
        Set the barcode (must be 13 digits) and load product information.

        Args:
            value: The barcode string.

        Raises:
            ValueError: If the barcode does not contain exactly 13 digits.
        """
        value_str = str(value)
        if not value_str.isdigit() or len(value_str) != 13:
            raise ValueError("Штрих-код должен содержать ровно 13 цифр")
        self._barcode = value_str
        self._load_info_from_barcode()

    @property
    def name(self) -> str:
        """Return the product name."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def country(self) -> str:
        """Return the country of origin."""
        return self._country

    @country.setter
    def country(self, value: str) -> None:
        self._country = value

    @property
    def price(self) -> float:
        """Return the product price."""
        return self._price

    @price.setter
    def price(self, value: float) -> None:
        """
        Set the product price.

        Args:
            value: New price.

        Raises:
            ValueError: If the price is negative.
        """
        if value < 0:
            raise ValueError("Цена не может быть отрицательной")
        self._price = value

    @property
    def manufacturer(self) -> str:
        """Return the manufacturer name."""
        return self._manufacturer

    @manufacturer.setter
    def manufacturer(self, value: str) -> None:
        self._manufacturer = value

    def _load_info_from_barcode(self) -> None:
        """
        Protected method: load product attributes from the global barcode_info.

        Raises:
            ValueError: If the barcode is not found in the reference data.
        """
        if self._barcode not in barcode_info:
            raise ValueError(f"Информация о товаре с кодом {self._barcode} не найдена")
        info = barcode_info[self._barcode]
        self._name = info.get('name', 'Неизвестно')
        self._country = info.get('country', 'Неизвестно')
        self._price = info.get('price', 0.0)
        self._manufacturer = info.get('manufacturer', 'Неизвестно')

    def __repr__(self) -> str:
        """Return a developer‑friendly string representation."""
        return f"Product({self._barcode}, {self._name}, {self._price} руб.)"


# ----------------------------------------------------------------------
# Cart class with file‑based persistence
# ----------------------------------------------------------------------
class Cart:
    """
    Shopping cart that stores a list of Product instances.

    The cart automatically loads its contents from a JSON file on initialisation
    and saves after every modification.
    """

    def __init__(self, cart_file: str = "cart.json"):
        """
        Initialise the cart.

        Args:
            cart_file: Path to the JSON file used for persistence.
        """
        self._items = []          # List of Product objects
        self._total_price = 0.0
        self._cart_file = cart_file
        self._load()              # Attempt to restore a previously saved cart

    @property
    def total_price(self) -> float:
        """Return the total price of all products in the cart."""
        return self._total_price

    @property
    def items(self):
        """
        Return a copy of the product list to prevent external modification.

        Returns:
            list: A shallow copy of the internal product list.
        """
        return self._items.copy()

    def _update_total(self) -> None:
        """Protected method: recalculate the total price."""
        self._total_price = sum(item.price for item in self._items)

    def add_product(self, product: Product) -> None:
        """
        Add a product to the cart and persist the change.

        Args:
            product: The Product instance to add.
        """
        self._items.append(product)
        self._update_total()
        self._save()

    def remove_product(self, barcode: str) -> bool:
        """
        Remove the first product matching the given barcode.

        Args:
            barcode: The barcode of the product to remove.

        Returns:
            True if a product was removed, False otherwise.
        """
        barcode_str = str(barcode)
        for i, item in enumerate(self._items):
            if item.barcode == barcode_str:
                del self._items[i]
                self._update_total()
                self._save()
                return True
        return False

    def show_contents(self) -> None:
        """Print the current cart contents and total price."""
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
        """Protected method: save the list of barcodes to the JSON file."""
        barcodes = [item.barcode for item in self._items]
        with open(self._cart_file, 'w', encoding='utf-8') as f:
            json.dump(barcodes, f, ensure_ascii=False, indent=2)

    def _load(self) -> None:
        """
        Protected method: load barcodes from the JSON file and reconstruct products.

        If the global barcode_info is not yet loaded, restoration is impossible
        and the cart remains empty.
        """
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
                # Creating a Product requires the global barcode_info
                items.append(Product(bc))
            except ValueError as e:
                print(f"Не удалось загрузить товар {bc}: {e}")
        self._items = items
        self._update_total()


# ----------------------------------------------------------------------
# Helper functions for loading the barcode reference and catalog
# ----------------------------------------------------------------------
def load_barcode_info(info_file: str = "barcode_info.json") -> None:
    """
    Load the barcode reference dictionary from a JSON file into the global variable.

    Args:
        info_file: Path to the JSON file.

    Raises:
        FileNotFoundError: If the specified file does not exist.
    """
    global barcode_info
    if not os.path.exists(info_file):
        raise FileNotFoundError(f"Файл {info_file} не найден. Невозможно расшифровать штрих-коды.")
    with open(info_file, 'r', encoding='utf-8') as f:
        barcode_info = json.load(f)
    print(f"Справочник штрих-кодов загружен (записей: {len(barcode_info)}).")


def load_catalog(catalog_file: str) -> None:
    """
    Load the list of available product barcodes from a JSON file into the global set.

    Args:
        catalog_file: Path to the JSON file containing a list of barcodes.
    """
    global available_barcodes
    if not os.path.exists(catalog_file):
        print(f"Файл {catalog_file} не найден.")
        return
    with open(catalog_file, 'r', encoding='utf-8') as f:
        barcodes_list = json.load(f)
    available_barcodes = set(str(bc) for bc in barcodes_list)
    print(f"Загружено доступных товаров: {len(available_barcodes)}.")


# ----------------------------------------------------------------------
# Demonstration menu
# ----------------------------------------------------------------------
def main() -> None:
    """Main interactive menu for the shopping cart system."""
    # Pre‑load the barcode reference (mandatory)
    try:
        load_barcode_info()
    except FileNotFoundError as e:
        print(e)
        return

    # Create the cart (it will attempt to load a previous state)
    cart = Cart("cart.json")

    # Main menu loop
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
