from django.contrib import admin
from .models import Proj
from .models import Folders
from .models import Cases
from .models import Launches
from .models import LaunchedCases
from .models import TestRunResult

admin.site.register(Proj)
admin.site.register(Folders)
admin.site.register(Cases)
admin.site.register(Launches)
admin.site.register(LaunchedCases)
admin.site.register(TestRunResult)