from django.db.models import Q, QuerySet

from .permissions import permission_is_exempt


class RestrictedQuerySet(QuerySet):

    def restrict(self, user, action='view'):
        """
         Filtre o QuerySet para retornar apenas objetos nos quais o usuário especificado recebeu o especificado
         permissão.

         :param user: instância do usuário
         :param action: A ação que deve ser permitida (por exemplo, "view" para "dcim.view_site"); o padrão é 'visualizar'
         """
        # Resolva o nome completo da permissão necessária
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        permission_required = f'{app_label}.{action}_{model_name}'

        # Ignorar restrição para superusuários e visualizações isentas
        if user.is_superuser or permission_is_exempt(permission_required):
            qs = self

        # O usuário é anônimo ou não recebeu a permissão necessária
        elif not user.is_authenticated or permission_required not in user.get_all_permissions():
            qs = self.none()

        # Filtre o queryset para incluir apenas objetos com atributos permitidos
        else:
            attrs = Q()
            for perm_attrs in user._object_perm_cache[permission_required]:
                if type(perm_attrs) is list:
                    for p in perm_attrs:
                        attrs |= Q(**p)
                elif perm_attrs:
                    attrs |= Q(**perm_attrs)
                else:
                    # Qualquer permissão com restrições nulas concede acesso a _all_ instâncias
                    attrs = Q()
                    break
            else:
                # para outro, quando não há pausa
                 # evite duplicatas quando JOIN em campos muitos para muitos sem usar DISTINCT.
                 # DISTINCT atua globalmente em toda a solicitação, o que pode não ser desejável.
                allowed_objects = self.model.objects.filter(attrs)
                attrs = Q(pk__in=allowed_objects)
            qs = self.filter(attrs)

        return qs
