from django.contrib import admin
from .models import Proj
from .models import Folders
from .models import CaseStoreStatuses
from .models import Cases

admin.site.register(Proj)
admin.site.register(Folders)
admin.site.register(CaseStoreStatuses)
admin.site.register(Cases)