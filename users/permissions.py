from django.conf import settings
from django.contrib.contenttypes.models import ContentType


def get_permission_for_model(model, action):
    """
     Resolva a permissão nomeada para um determinado modelo (ou instância) e ação (por exemplo, visualizar ou adicionar).

     :param model: Um modelo ou instância
     :param ação: Exibir, adicionar, alterar ou excluir (string)
     """
    return '{}.{}_{}'.format(
        model._meta.app_label,
        action,
        model._meta.model_name
    )


def resolve_permission(name):
    """
     Dado um nome de permissão, retorne os componentes app_label, action e model_name. Por exemplo, "dcim.view_site"
     retorna ("dcim", "view", "site").

     :param name: nome da permissão no formato <app_label>.<action>_<model>
     """
    try:
        app_label, codename = name.split('.')
        action, model_name = codename.rsplit('_', 1)
    except ValueError:
        raise ValueError(
            f"Nome de permissão inválido: {name}. Deve estar no formato <app_label>.<action>_<model>"
        )

    return app_label, action, model_name


def resolve_permission_ct(name):
    """
     Dado um nome de permissão, retorne o ContentType e a ação relevantes. Por exemplo, "dcim.view_site" retorna
     (Site, "visualizar").

     :param name: nome da permissão no formato <app_label>.<action>_<model>
     """
    app_label, action, model_name = resolve_permission(name)
    try:
        content_type = ContentType.objects.get(app_label=app_label, model=model_name)
    except ContentType.DoesNotExist:
        raise ValueError(f"App_label/model_name desconhecido para {name}")

    return content_type, action


def permission_is_exempt(name):
    """
     Determine se uma permissão especificada está isenta de avaliação.

     :param name: nome da permissão no formato <app_label>.<action>_<model>
     """
    app_label, action, model_name = resolve_permission(name)

    if action == 'view':
        if (
            # All models (excluding those in EXEMPT_EXCLUDE_MODELS) are exempt from view permission enforcement
            '*' in settings.EXEMPT_VIEW_PERMISSIONS and (app_label, model_name) not in settings.EXEMPT_EXCLUDE_MODELS
        ) or (
            # This specific model is exempt from view permission enforcement
            f'{app_label}.{model_name}' in settings.EXEMPT_VIEW_PERMISSIONS
        ):
            return True

    return False
