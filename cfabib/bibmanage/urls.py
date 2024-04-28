from django.urls import path

from . import views

urlpatterns = [
    path('', views.bmindex, name='bmindex'),
    path('add', views.add, name='add'),
    path('batch', views.batch, name='batch'),
    path('batch/<int:batchid>', views.viewbatch, name='viewbatch'),
    path('export', views.export, name='export'),
    path('close_batch', views.close_batch, name='close_batch'),
    path('post_openbatch',views.post_openbatch, name='post_openbatch'),
    path('post_addtobatch',views.post_addtobatch, name='post_addtobatch'),
    #path('add_post', views.add_post, name='add_post'),
    path('delete_post', views.delete_post, name='delete_post'),
    path('select_criteria', views.select_criteria, name='select_criteria'),

    path('info', views.info, name='info'),
    path('tips', views.tips, name='tips'),

    # path('eval_articles', views.eval_articles, name='eval_articles'),
    #path('results', views.results, name='results'),
    #submit to ads
    path('submitads', views.submitads, name='submitads'),
]