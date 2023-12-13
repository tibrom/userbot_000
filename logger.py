import logging


# Создаем и настраиваем логгер
logger = logging.getLogger("dev_logger")
logger.setLevel(logging.DEBUG)

# Создаем обработчик (handler) для записи логов в файл
file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.DEBUG)

# Создаем обработчик (handler) для вывода логов на консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Создаем форматер для определения формата записей в логе
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Добавляем обработчики в логгер
#logger.addHandler(file_handler)
logger.addHandler(console_handler)