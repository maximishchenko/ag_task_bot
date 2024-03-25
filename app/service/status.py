"""Описание различных статусов приложения.

Используются статусы записей в БД и операции по их модификации.
"""


class Status:
    """Константы возможных статусов."""

    active = 1
    inactive = 0


class StatusAction:
    """Константы действий статусов."""

    act_enable_user = "act_enable_user"
    act_disable_user = "act_disable_user"
