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
        self.last_update_date = timezone.now() #при апдейде проекта ластовой датой апдейта ставится время прожатия кнопки
        self.save()

    def __str__(self):
        return self.title
 
class Folders(models.Model):
    name = models.CharField(max_length=100)
    level=models.SmallIntegerField()
    project=models.ForeignKey(Proj, on_delete=models.CASCADE)
    #у папки могут быть родители/дети
    parent_folder = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        verbose_name="Родительская папка",
        related_name='subfolders',
        null=True,
        blank=True
    ) 

    def __str__(self):
        return self.name
    
class Cases(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)

    status = [
        ('Черновик'),
        ('На ревью'),
        ('Актуальный'),
        ('Требует доработки')
    ]

    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    folder = models.ForeignKey(Folders, on_delete=models.CASCADE, related_name="cases_folder")

    def __str__(self):
        return self.title

#хранит информацию по запуску в целом
class Launches(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    project = models.ForeignKey(Proj, on_delete=models.CASCADE)

    STATUS_CHOICES = [
        ('in_progress' , 'В процессе'),
        ('completed' , 'Завершен')
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='В процессе')
    assignees = models.CharField(max_length=1000, default="default tester")
    created_date = models.DateTimeField(default=timezone.now)
    finish_date = models.DateTimeField(default=timezone.now)

    total_cases = models.PositiveIntegerField(default=0, verbose_name="Всего кейсов")
    passed_cases = models.PositiveIntegerField(default=0, verbose_name="Пройдено")
    failed_cases = models.PositiveIntegerField(default=0, verbose_name="Провалено")
    unknown_cases = models.PositiveIntegerField(default=0, verbose_name="Неизвестных")
    skipped_cases = models.PositiveIntegerField(default=0, verbose_name="Пропущенных")
    correction_needed_cases = models.PositiveIntegerField(default=0, verbose_name="Требует правки")

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def add_test_case(self, test_case):
        """Добавление тест-кейса в запуск"""
        TestRunResult.objects.get_or_create(
            test_run=self,
            test_case=test_case,
            defaults={'status': 'not_run'}
        )

#хранит результаты прохождения и инфу по каждому пройденному кейсу в запуске
class TestRunResult(models.Model):
    testCase = models.ForeignKey(Cases, on_delete=models.CASCADE)
    launch = models.ForeignKey(Launches, on_delete=models.CASCADE, null=True)
    """
    Результат выполнения конкретного тест-кейса в рамках запуска
    """
    STATUS_CHOICES = [
        ('passed' , 'успешный'),
        ('failed' , 'проваленный'),
        ('unknown' , 'неизвестный'),
        ('skipped' , 'пропущенный'),
        ('correction_needed' , 'кейс требует правки')
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='not_run',
        verbose_name="Статус выполнения"
    )
    
    # Детали выполнения
    executed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    executed_at = models.DateTimeField(
        verbose_name="Дата выполнения",
        null=True,
        blank=True
    )
    
    # Комментарии и приложения
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    attachment = models.FileField(
        upload_to='test_run_attachments/',
        verbose_name="Приложение",
        null=True,
        blank=True
    )
    
    # Время выполнения (в минутах)
    execution_time = models.PositiveIntegerField(
        default=0,
        verbose_name="Время выполнения (минуты)"
    )
    
    # Связь с дефектом (если тест упал)
    defect_url = models.URLField(blank=True, verbose_name="Ссылка на дефект")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    # def __str__(self):
    #     return self.title

    # def clean(self):
    #     # Нельзя установить executed_by без executed_at и наоборот
    #     if bool(self.executed_by) != bool(self.executed_at):
    #         raise ValidationError("Поля 'Выполнил' и 'Дата выполнения' должны быть заполнены одновременно")

    # def save(self, *args, **kwargs):
    #     # Автоматически устанавливаем executed_at при изменении статуса на выполненный
    #     if self.status in ['passed', 'failed', 'blocked'] and not self.executed_at:
    #         self.executed_at = timezone.now()
        
    #     # Если статус сброшен на not_run, очищаем executed_at и executed_by
    #     if self.status == 'not_run':
    #         self.executed_at = None
    #         self.executed_by = None
        
    #     self.full_clean()
    #     super().save(*args, **kwargs)
        
    #     # Обновляем метрики родительского запуска
    #     self.test_run.save()