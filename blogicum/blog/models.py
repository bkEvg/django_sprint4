from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

from core.constants import MAX_LENGTH_CHAR_FIELD


User = get_user_model()


class BaseModel(models.Model):
    """Base model describes fields for every class such as:
    * is_published - Опубликовано
    * created_at - Добавлено
    """

    is_published = models.BooleanField(default=True,
                                       verbose_name='Опубликовано',
                                       help_text='Снимите галочку, '
                                                 'чтобы скрыть публикацию.')
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Добавлено')

    class Meta:
        """Meta class"""

        abstract = True


class Post(BaseModel):
    """class representing 'Post' fields in database"""

    title = models.CharField(max_length=MAX_LENGTH_CHAR_FIELD,
                             verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(verbose_name='Дата и время публикации',
                                    help_text='Если установить дату и время '
                                              'в будущем — можно делать '
                                              'отложенные публикации.',)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор публикации')
    location = models.ForeignKey('Location', on_delete=models.SET_NULL,
                                 blank=True, null=True,
                                 verbose_name='Местоположение')
    category = models.ForeignKey('Category', on_delete=models.SET_NULL,
                                 null=True,
                                 verbose_name='Категория',
                                 related_name='posts')

    class Meta:
        """Meta class"""

        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        """String representation"""
        return self.title

    def get_absolute_url(self):
        """Get absolute path to the element"""
        return reverse('blog:post_detail', kwargs={'pk': self.pk})

    @staticmethod
    def comment_count(self):
        return self.comments.count()


class Category(BaseModel):
    """class representing 'Category' fields in database"""

    title = models.CharField(max_length=MAX_LENGTH_CHAR_FIELD,
                             verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(unique=True, verbose_name='Идентификатор',
                            help_text='Идентификатор страницы для URL; '
                                      'разрешены символы латиницы, цифры, '
                                      'дефис и подчёркивание.')

    class Meta:
        """Meta class"""

        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        """String representation"""
        return self.title


class Location(BaseModel):
    """Class representing 'Location' fields in database"""

    name = models.CharField(max_length=MAX_LENGTH_CHAR_FIELD,
                            verbose_name='Название места')

    class Meta:
        """Meta class"""

        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self) -> str:
        """String representation"""
        return self.name


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments',
                             on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        """Meta class"""

        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self) -> str:
        return f"комментарий от {self.author.username} на {self.post.title}"
