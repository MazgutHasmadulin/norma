## Быстрый контекст репозитория

Проект — обычное Django-приложение:
- root-проект: `mysite` (файл настроек: `mysite/settings.py`)
- приложение: `norma` (модельно-логическая часть в `norma/`)
- БД: SQLite по умолчанию (`db.sqlite3`), зависимости в `requirements.txt` (Django ~= 5.1.x)

Основная цель инструкций — дать AI агента быстрый «контекстовый снимок», чтобы правки были корректными и минимально инвазивными.

## Ключевые файлы и шаблоны (быстрые ссылки)
- `mysite/settings.py` — конфигурация (используется `bootstrap5` в `INSTALLED_APPS`, `STATIC_ROOT`, локаль `ru-ru`).
- `mysite/urls.py` — подключает `norma.urls` на корневом пути.
- `norma/models.py` — основные модели: `Proj`, `Folders`, `Cases`, `Launches`, `TestRunResult`.
- `norma/views.py` — CRUD-операции над проектами/папками/кейсам; есть примеры `prefetch_related`.
- `norma/forms.py` — формы: `ProjCreationForm`, `CaseCreationForm`, `FolderCreationForm`.
- `norma/urls.py` — маршруты приложения (обратить внимание на опечатки, см. ниже).
- `norma/templates/norma/` — шаблоны: `proj_list.html`, `proj_edit.html`, `cases_list.html`, `case_detail.html` и т.д.
- `requirements.txt` — содержит `Django~=5.1.2`.
- `test_run_attachments/` — директория для загрузок, используется в `TestRunResult.attachment`.

## Архитектура и паттерны (чем полезно следовать)
- Это классический серверный рендеринг Django: views формируют контекст и возвращают `render(request, template, ctx)`.
- Формы создаются как `ModelForm` и используются в view-функциях с паттерном `if request.method == "POST": ... else: form = ...`.
- Модели содержат связи ForeignKey с `settings.AUTH_USER_MODEL` для автора.
- В `cases_list` показан пример оптимизации запросов: `Prefetch` для загрузки кейсов вместе с папками — предпочитайте похожую предзагрузку для списков.

## Проект-специфичные соглашения и замечания
- Поля дат: проект явно использует `timezone.now()` при создании и для `last_update_date`.
- Многие view-функции временно рендерят единый шаблон `proj_edit.html` (комментарии в коде указывают, что это стоит поменять) — при правках форм учитывайте, что шаблон может быть «заглушкой».
- В моделях и статусах часто используются русские метки в choices; при изменении кода интерфейса сохраняя/сравнивайте с техническими ключами (например, `'draft'`, `'actual'`).
- Есть явная опечатка в `norma/urls.py`: строки вида `path('folders/int:pk/edit', ...)` должны быть `path('folders/<int:pk>/edit', ...)`. Исправляйте такие баги аккуратно и запускайте тест / runserver.

## Важные рабочие команды (локальная разработка)
- Установка зависимостей: создать виртуальное окружение и `pip install -r requirements.txt`.
- Применить миграции: `python manage.py migrate`.
- Запустить dev-сервер: `python manage.py runserver`.
- Создать суперпользователя: `python manage.py createsuperuser`.
- Тесты: `python manage.py test` (в данный момент `norma/tests.py` пустой).

Если изменения затрагивают загрузку media/static — помните про `STATIC_ROOT` в `settings.py` и поле `upload_to='test_run_attachments/'`.

## Примеры, которые полезно показывать при правках
- Добавление/редактирование проекта: `norma/views.py::proj_new` использует `ProjCreationForm` и затем `redirect('proj_dashboard', pk=proj.pk)`.
- Список кейсов с папками: `norma/views.py::cases_list` использует `Prefetch('cases_folder', queryset=Cases.objects.all().order_by('title'))` и собирает `cases_without_folder`.
- Модель кейса: `Cases.folder` имеет `related_name='cases_folder'` — учтите это при создании ORM-запросов.

## Чеклисты для AI при внесении правок
- Всегда запускать `python manage.py migrate` если добавлены/изменены модели.
- Если меняются URL-паттерны — корректировать соответствующие `redirect()` в views и проверять ссылки в шаблонах.
- Исправляя опечатки в `norma/urls.py` — убедиться, что шаблоны и `redirect()` используют корректные имена маршрутов.
- Для изменений, влияющих на загрузку/хранение файлов — проверить путь `test_run_attachments/` и `MEDIA`/`STATIC` настройки.

## Что НЕ менять автоматически
- Секретные ключи в `mysite/settings.py` (если вы не добавляете механизм безопасного хранения).
- Производственные настройки (DEBUG, ALLOWED_HOSTS) без явного указания человека.

## Где искать дополнительные подсказки
- Миграции: `norma/migrations/` — показывают историю изменений моделей.
- Шаблоны в `norma/templates/norma/` — примеры верстки и имён контекстных переменных.

Если что-то в этих инструкциях неполно или вы хотите, чтобы я добавил пример исправления (например, правку опечатки в `norma/urls.py` и быстрый запуск сервера), скажите — применю изменения и прогоню минимальную валидацию.
