from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    #path('', views.index, name='index'),
    path('', views.search, name='search'),
    
    # #account related
    # path("login", views.login_form, name="login_form"),
    # path("login_view", views.login_view, name="login_view"),
    # path("logout", views.logout_view, name="logout_view"),
    # path("account", views.account, name="account"),
    # path("register", views.register, name="register"),
    # path("registering", views.registering, name="registering"),

    #static
    path("help", views.help, name="help"),
    path("about", views.about, name="about"),

    #search related
    path('queued', views.queued, name='queued'),
    #path('search', views.search, name='search'),
    path('history', views.history, name='history'),
    path('<int:reid>', views.report, name='report'),
    path('sumqueue', views.sumqueue, name='sumqueue'),
    path('summaries', views.summaries, name='summaries'),
    path('summary/<int:reid>', views.summary, name='summary'),
    path('export_author', views.export_author, name='export_author'),
    path('export_journal', views.export_journal, name='export_journal'),
    path('export_summary', views.export_summary, name='export_summary'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)