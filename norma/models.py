from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

#проекты
class Proj(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    created_date = models.DateTimeField(default=timezone.now)
    #дата последнего апдейта по кейсам
    last_update_date = models.DateTimeField(default=timezone.now)
    #поле ниже под пользователей проекта, чтобы зайдя в проект ПМ или разработчики понимали, к кому можно обращаться
    #пока что думаю пользователи проекта=авторы кейсов, потому что пмы или разрабы не пишут кейсы, только ответственные за проект тестировщики
    personel=models.CharField(max_length=1000, default="untitled_author")

    def update(self):
        self.last_update_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title
 
class Folders(models.Model):
    name = models.CharField(max_length=100)
    level=models.SmallIntegerField()
    project=models.ForeignKey(Proj, on_delete=models.CASCADE)
    

class CaseStoreStatuses(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Cases(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    status = models.ForeignKey(CaseStoreStatuses, on_delete=models.CASCADE)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    folder_id = models.ForeignKey(Folders, on_delete=models.CASCADE, related_name="cases_folder")
    level = models.ForeignKey(Folders, on_delete=models.CASCADE, related_name="cases_level")


# class Project(models.Model):
#     """
#     Проект - корневая папка системы
#     """
#     name = models.CharField(max_length=255, verbose_name="Название проекта")
#     description = models.TextField(blank=True, verbose_name="Описание проекта")
#     author = models.ForeignKey(
#         User, 
#         on_delete=models.CASCADE, 
#         verbose_name="Автор проекта",
#         related_name='projects'
#     )
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
#     updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
#     level = models.PositiveIntegerField(default=0, verbose_name="Уровень вложенности")

#     class Meta:
#         verbose_name = "Проект"
#         verbose_name_plural = "Проекты"
#         ordering = ['-created_at']

#     def __str__(self):
#         return self.name

#     def save(self, *args, **kwargs):
#         # Проект всегда имеет уровень 0
#         self.level = 0
#         super().save(*args, **kwargs)

# class Folder(models.Model):
#     """
#     Папка - может содержать другие папки и тест-кейсы
#     """
#     name = models.CharField(max_length=255, verbose_name="Название папки")
#     description = models.TextField(blank=True, verbose_name="Описание папки")
#     author = models.ForeignKey(
#         User, 
#         on_delete=models.CASCADE, 
#         verbose_name="Автор папки",
#         related_name='folders'
#     )
#     project = models.ForeignKey(
#         Project,
#         on_delete=models.CASCADE,
#         verbose_name="Проект",
#         related_name='folders'
#     )
#     parent_folder = models.ForeignKey(
#         'self',
#         on_delete=models.CASCADE,
#         verbose_name="Родительская папка",
#         related_name='subfolders',
#         null=True,
#         blank=True
#     )
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
#     updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
#     level = models.PositiveIntegerField(default=1, verbose_name="Уровень вложенности")

#     class Meta:
#         verbose_name = "Папка"
#         verbose_name_plural = "Папки"
#         ordering = ['name']

#     def __str__(self):
#         return f"{self.name} (Уровень: {self.level})"

#     def clean(self):
#         # Валидация: папка не может быть своим собственным родителем
#         if self.parent_folder and self.parent_folder.id == self.id:
#             raise ValidationError("Папка не может быть своим собственным родителем")
        
#         # Валидация: максимальный уровень вложенности
#         if self.level > 10:
#             raise ValidationError("Превышен максимальный уровень вложенности")

#     def save(self, *args, **kwargs):
#         # Автоматически вычисляем уровень вложенности
#         if self.parent_folder:
#             self.level = self.parent_folder.level + 1
#         else:
#             self.level = 1
        
#         # Проверяем валидацию перед сохранением
#         self.full_clean()
#         super().save(*args, **kwargs)

# class TestCase(models.Model):
#     """
#     Тест-кейс - может находиться в проекте или папке любого уровня
#     """
#     STATUS_CHOICES = [
#         ('draft', 'Черновик'),
#         ('active', 'Активный'),
#         ('archived', 'Архивный'),
#     ]
    
#     PRIORITY_CHOICES = [
#         ('low', 'Низкий'),
#         ('medium', 'Средний'),
#         ('high', 'Высокий'),
#         ('critical', 'Критический'),
#     ]

#     title = models.CharField(max_length=500, verbose_name="Заголовок тест-кейса")
#     description = models.TextField(blank=True, verbose_name="Описание тест-кейса")
#     preconditions = models.TextField(blank=True, verbose_name="Предусловия")
#     steps = models.JSONField(verbose_name="Шаги тестирования", default=list)
#     expected_result = models.TextField(verbose_name="Ожидаемый результат")
#     actual_result = models.TextField(blank=True, verbose_name="Фактический результат")
    
#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default='draft',
#         verbose_name="Статус"
#     )
#     priority = models.CharField(
#         max_length=20,
#         choices=PRIORITY_CHOICES,
#         default='medium',
#         verbose_name="Приоритет"
#     )
    
#     author = models.ForeignKey(
#         User, 
#         on_delete=models.CASCADE, 
#         verbose_name="Автор тест-кейса",
#         related_name='test_cases'
#     )
#     project = models.ForeignKey(
#         Project,
#         on_delete=models.CASCADE,
#         verbose_name="Проект",
#         related_name='test_cases'
#     )
#     folder = models.ForeignKey(
#         Folder,
#         on_delete=models.CASCADE,
#         verbose_name="Папка",
#         related_name='test_cases',
#         null=True,
#         blank=True
#     )
    
#     # Связь многие-ко-многим для связанных тест-кейсов
#     related_cases = models.ManyToManyField(
#         'self',
#         verbose_name="Связанные тест-кейсы",
#         blank=True,
#         symmetrical=False
#     )
    
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
#     updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
#     level = models.PositiveIntegerField(default=1, verbose_name="Уровень вложенности")

#     class Meta:
#         verbose_name = "Тест-кейс"
#         verbose_name_plural = "Тест-кейсы"
#         ordering = ['-created_at']

#     def __str__(self):
#         return f"{self.title} (Приоритет: {self.get_priority_display()})"

#     def clean(self):
#         # Валидация: тест-кейс должен принадлежать либо папке, либо проекту напрямую
#         if not self.folder and not self.project:
#             raise ValidationError("Тест-кейс должен принадлежать либо папке, либо проекту")

#     def save(self, *args, **kwargs):
#         # Автоматически вычисляем уровень вложенности
#         if self.folder:
#             self.level = self.folder.level + 1
#         else:
#             self.level = 1
        
#         # Проверяем валидацию перед сохранением
#         self.full_clean()
#         super().save(*args, **kwargs)

#     def get_full_path(self):
#         """
#         Возвращает полный путь к тест-кейсу в иерархии
#         """
#         path_parts = []
        
#         if self.folder:
#             current_folder = self.folder
#             while current_folder:
#                 path_parts.insert(0, current_folder.name)
#                 current_folder = current_folder.parent_folder
        
#         path_parts.insert(0, self.project.name)
#         path_parts.append(self.title)
        
#         return " / ".join(path_parts)

# class TestStep(models.Model):
#     """
#     Детальная модель для шагов тест-кейса (опционально, для более сложной структуры)
#     """
#     test_case = models.ForeignKey(
#         TestCase,
#         on_delete=models.CASCADE,
#         verbose_name="Тест-кейс",
#         related_name='test_steps'
#     )
#     step_number = models.PositiveIntegerField(verbose_name="Номер шага")
#     action = models.TextField(verbose_name="Действие")
#     expected_result = models.TextField(verbose_name="Ожидаемый результат")
#     actual_result = models.TextField(blank=True, verbose_name="Фактический результат")
    
#     class Meta:
#         verbose_name = "Шаг тест-кейса"
#         verbose_name_plural = "Шаги тест-кейса"
#         ordering = ['step_number']
#         unique_together = ['test_case', 'step_number']

#     def __str__(self):
#         return f"Шаг {self.step_number} для {self.test_case.title}"