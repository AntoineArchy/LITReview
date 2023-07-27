from django.conf import settings
from django.db import models


class UserFollows(models.Model):
    """
    Permet la création de relations entre les utilisateurs.
    """
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='following')
    followed_user = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                                      on_delete=models.CASCADE,
                                      related_name='followed_by')

    class Meta:
        """
        S'assure que chaque couple utilisateur abonné/utilisateur suivi est unique
        """
        unique_together = ('user', 'followed_user',)
