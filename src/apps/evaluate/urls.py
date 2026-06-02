from django.urls import path
from . import views

app_name = "evaluate"

urlpatterns = [
    path("evaluate/", views.evaluation_dashboard, name="dashboard"),
    path("evaluate/qa-setup/<str:project_id>/", views.qa_setup, name="qa_setup"),
    path("evaluate/qa-status/<str:project_id>/", views.qa_generation_status, name="qa_status"),
    path("evaluate/run/<str:project_id>/", views.run_evaluation, name="run_evaluation"),
    path("evaluate/run-status/<uuid:run_id>/", views.evaluation_run_status, name="run_status"),
    path("evaluate/results/<uuid:run_id>/", views.evaluation_results, name="results"),
    path("evaluate/qa-item/<uuid:item_id>/delete/", views.delete_qa_item, name="delete_qa_item"),
]
