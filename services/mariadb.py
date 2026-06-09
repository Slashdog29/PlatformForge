"""
Gestor de MariaDB (alias con algunas diferencias mínimas).
En Arch, mariadb es el paquete que provee MySQL, por lo que este gestor
hereda de MysqlManager para evitar duplicación.
"""
from services.mysql import MysqlManager


class MariadbManager(MysqlManager):
    """
    MariaDB comparte implementación con MySQL en Arch.
    """
    pass