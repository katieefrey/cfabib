from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    #login/out
    path("login", views.login_form, name="login_form"),
    path("login_view", views.login_view, name="login_view"),
    path("logout", views.logout_view, name="logout_view"),
    path("account", views.account, name="account"),
    path("account/<int:year>/<int:month>/<int:day>", views.history, name="history"),
    #edit entries
    path('batch', views.batch, name='batch'),

    #path('massupdate/<int:year>/<int:month>', views.massupdate, name='massupdate'),
    #path('post_massupdate', views.post_massupdate, name='post_massupdate'),
    
    path('update/<int:year>/<int:month>', views.update, name='update'),
    path('unknown/<int:year>/<int:month>', views.unknown, name='unknown'),
    
    path('post_update', views.post_update, name='post_update'),

    path('nameupdate/<int:year>/<int:month>', views.nameupdate, name='nameupdate'),
    path('nameunknown/<int:year>/<int:month>', views.nameunknown, name='nameunknown'),
    path('nameverify/<int:year>/<int:month>', views.nameverify, name='nameverify'),
    path('post_nameupdate', views.post_nameupdate, name='post_nameupdate'),
    path('post_nameverify', views.post_nameverify, name='post_nameverify'),


    path('nameverified/<int:year>/<int:month>', views.nameverified, name='nameverified'),
    path('nameupdated/<int:year>/<int:month>', views.nameupdated, name='nameupdated'),

    path('bibcode/<bib>',views.bibcode, name='bibcode'),

    #path('nameverifyalt/<int:year>/<int:month>', views.nameverifyalt, name='nameverifyalt'),
    ]
    