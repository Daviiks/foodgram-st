#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import argparse


def set_debug_mode(mode):
    """Устанавливает режим DEBUG в переменных окружения."""
    debug_value = "1" if mode == "dev" else "0"
    os.environ["DEBUG"] = debug_value
    print(f"Режим установлен: {'DEBUG' if debug_value == '1' else 'PRODUCTION'}")


def parse_args():
    """Парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(description="Запуск Django с выбором режима.")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["dev", "prod"],
        default="dev",
        help="Режим запуска: dev (DEBUG=True) или prod (DEBUG=False)",
    )
    return parser.parse_known_args()


def main():
    """Основная логика запуска."""
    args, unknown_args = parse_args()
    set_debug_mode(args.mode)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Передаём оставшиеся аргументы в Django
    execute_from_command_line([sys.argv[0]] + unknown_args)


if __name__ == '__main__':
    main()