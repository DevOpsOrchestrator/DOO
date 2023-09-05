#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doo.settings')

    from django.conf import settings

    if settings.DEBUG:
        if os.environ.get('DJANGO_DEBUG','False').lower() in ('true','yes','1','t','y') and 'runserver' in sys.argv:
            import debugpy

            try:
                print('DEBUG ESCUTANDO NA PORTA 3000!')
                debugpy.listen(("0.0.0.0", 3000))
                debugpy.wait_for_client()
                print('Attached!')
            except Exception as erro:
                pass

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
