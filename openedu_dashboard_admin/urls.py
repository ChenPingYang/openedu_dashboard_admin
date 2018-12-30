"""openedu_dashboard_admin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from . import view
from try1.views import C_T
from index.views import index_view
from BasicCourseData.views import basic_course_data_view
from MovieData.views import movie_data_view
from ForumData.views import forum_data_view
from practive.views import practive_view
from Glossary.views import glossary_view
from AnalysisStudent.views import analysis_student_view
from AnalysisGroup.views import analysis_group_view
from AnalysisCourse.views import analysis_course_view
from AnalysisData.views import analysis_data_view
from certificate.views import certificate_view
from AfterSurvey.views import after_survey_view
from BeforeSurvey.views import before_survey_view
from ErrorReport.views import error_report_view
from AnalysisForum.views import analysis_forum_view
from PopularCourse.views import popular_courses_education_view, popular_courses_age_view
from ChartData.views import chart_data_view
from AnalysisVideo.views import analysis_video_view
from CourseOverview.views import course_overview_view


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^test/', C_T),
    url(r'^index/', index_view, name='index'),
    url(r'^BasicCourseDataServlet/', basic_course_data_view, name='BasicCourseDataServlet'),
    url(r'^MovieDataServlet/', movie_data_view, name='MovieDataServlet'),
    url(r'^ForumDataServlet/', forum_data_view, name='ForumDataServlet'),
    url(r'^practiveServlet', practive_view, name='practiveServlet'),
    url(r'^glossary', glossary_view, name='glossary'),
    url(r'^AnalysisStudentServlet', analysis_student_view, name='AnalysisStudentServlet'),
    url(r'^AnalysisGroupServlet', analysis_group_view, name='AnalysisGroupServlet'),
    url(r'^AnalysisCourseServlet', analysis_course_view, name='AnalysisCourseServlet'),
    url(r'^analysisServlet', analysis_data_view, name='analysisServlet?select=2'),
    url(r'^BeforeSurveyServlet/', before_survey_view, name='BeforeSurveyServlet'),
    url(r'^AfterSurveyServlet/', after_survey_view, name='AfterSurveyServlet'),
    url(r'^certificateServlet/', certificate_view, name='certificateServlet'),
    url(r'^ErrorReportServlet/', error_report_view, name='ErrorReportServlet'),
    url(r'^AnalysisDiscussion/', analysis_forum_view),
    url(r'^PopularCourseAge/', popular_courses_age_view),
    url(r'^PopularCourseEducation/', popular_courses_education_view),
    url(r'^ChartDataServlet/', chart_data_view),
    url(r'^AnalysisVideoServlet/', analysis_video_view),
    url(r'^CourseOverviewServlet/', course_overview_view),
]
