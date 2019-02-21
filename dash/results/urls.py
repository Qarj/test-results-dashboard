from django.urls import path

from . import views

app_name = 'results'
urlpatterns = [
    # ex: /results/
    path('', views.index, name='index'),

    # ex: /results/5/
    path('<int:result_id>/', views.detail, name='detail'),

    # ex: /results/log/?test_name=simple%20test
    path('log/', views.log, name='log'),

    # ex: /results/log_file/?test_name=simple%20test
    path('log_file/', views.log_file, name='log_file'),

    # ex: /results/run/My_Run/
    path('run/<run_name>/', views.run, name='run'),

    # ex: /results/app/My_App/
    path('app/<app_name>/', views.app, name='app'),

    # ex: /results/team/My_Team/
    path('team/<team_name>/', views.team, name='team'),

    # ex: /results/app/My_App/TeamCity/
    path('app/<app_name>/<run_server>/', views.app, name='app'),

    # ex: /results/delete/5/
    path('delete/<int:result_id>/', views.delete, name='delete'),

    # ex: /results/delete_oldest_runs_only_keep_newest/50/
    path('delete_oldest_runs_only_keep_newest/<int:number_of_runs_to_keep>/'
        , views.delete_oldest_runs_only_keep_newest
        , name='delete_oldest_runs_only_keep_newest'),

    # ex: /results/latest/
    path('latest/', views.latest, name='latest'),

    # ex: /results/latest/TeamCity
    path('latest/<run_server>/', views.latest, name='latest'),
]