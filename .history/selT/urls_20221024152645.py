from django.urls import path, include
from .views import CollegePredictionEventAPI, CollegePredictionAPI, CollegeEventAPI, CollegeFilterAPI, CollegeAPI, HighSchoolWeightAPI, UploadCSVAPI, HighSchoolAPI

urlpatterns = [
    path('upload', UploadCSVAPI.as_view({'get': 'list', 'post': 'create'}), name='upload'),
    path('highschool', HighSchoolAPI.as_view({'get': 'list'}), name='highschool'),
    path('highschoolweight', HighSchoolWeightAPI.as_view({'post': 'create'}), name='highschoolweight'),
    path('college-prediction-event', CollegePredictionEventAPI.as_view({'post': 'create'}), name='collegepercentage-event'),
    path('college-prediction', CollegePredictionAPI.as_view({'put': 'update'}), name='collegepercentage'), 
    path('college-event', CollegeEventAPI.as_view({'get': 'list'}), name='college-event'),
    path('college-filter', CollegeFilterAPI.as_view({'get': 'list'}), name='college'),
    path('college', CollegeAPI.as_view({'get': 'list'}), name='college')
]