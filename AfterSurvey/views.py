from django.shortcuts import render
from django.db import DatabaseError
from django.db import connections
from use_function import namedtuplefetchall, getCourseData
import ast


# Create your views here.
def after_survey_view(request):
    request.encoding = 'utf-8'
    request.GET = request.GET.copy()
    request.POST = request.POST.copy()
    to_render = {}

    if request.method == 'GET':
        courseNumber = 0
        surveyNumber  = 0
        data = None
        allCourseID = []
        count = 0

        with connections['SurveyDB'].cursor() as cursor:
            # 取得course_total_data_v2 更新日期
            cursor.execute("SELECT max(統計日期) as date FROM edxresult.course_total_data_v2")
            result = namedtuplefetchall(cursor)

            update_course_total_data = result[-1].date

            # 找出所有課程的id(不重複)
            cursor.execute(
                "SELECT DISTINCT(RR.course_id) "
                "FROM survey.recent_report as RR,edxresult.course_total_data_v2 as CTD "
                "WHERE RR.survey_id = '15'  && RR.course_id = CTD.course_id && CTD.統計日期 = %s order by RR.course_id",
                [update_course_total_data]
            )
            result = namedtuplefetchall(cursor)

            courseNumber = len(result)

            data = [['' for i in range(8)] for i in range(courseNumber)]

            for rs in result:
                allCourseID.append(rs.course_id)

            cursor.execute(
                "SELECT RR.course_id,RR.questions "
                "FROM survey.recent_report as RR,edxresult.course_total_data_v2 as CTD "
                "WHERE RR.survey_id = '15' && RR.course_id = CTD.course_id && CTD.統計日期 = %s order by RR.course_id",
                [update_course_total_data]
            )
            result = namedtuplefetchall(cursor)

            for rs in result:
                CourseData = getCourseData(rs.course_id)
                data[count][0] = CourseData[0]
                data[count][1] = CourseData[1]
                data[count][3] = CourseData[2]
                data[count][2] = rs.course_id
                break

            count = 0
            data[count][6] = '0'
            data[count][7] = '0'

            for i in range(len(result)):
                if result[i].course_id == allCourseID[count]:
                    selection1 = 0
                    selection2 = 0

                    json = result[i].questions
                    json = json[1:-1]
                    json = json.replace('false', 'False')
                    json = json.replace('true', 'True')
                    jsonFirstArray = ast.literal_eval(json)
                    jsonProblem = jsonFirstArray['problems']

                    jsonQuestionOne = jsonProblem[0]
                    selection1 = int(jsonQuestionOne['select'])

                    jsonQuestionTwo = jsonProblem[1]
                    selection2 = int(jsonQuestionTwo['select'])

                    surveyNumber = surveyNumber + 1

                    data[count][6] = str(int(data[count][6]) + (selection1 - 5) * (-1))
                    data[count][7] = str(int(data[count][7]) + (selection2 - 5) * (-1))
                else:
                    data[count][4] = str(surveyNumber)
                    data[count][5] = '{:.1f}'.format(surveyNumber / int(data[count][3]) * 100) + '%'
                    if surveyNumber == 0:
                        surveyNumber = 1

                    data[count][6] = '{:.1f}'.format(int(data[count][6]) / surveyNumber)
                    data[count][7] = '{:.1f}'.format(int(data[count][7]) / surveyNumber)

                    count = count + 1

                    CourseData = getCourseData(result[i].course_id)
                    data[count][0] = CourseData[0]
                    data[count][1] = CourseData[1]
                    data[count][3] = CourseData[2]
                    data[count][2] = result[i].course_id
                    data[count][6] = '0'
                    data[count][7] = '0'
                    surveyNumber = 0
                    i = i - 1

            data[count][4] = str(surveyNumber)
            data[count][5] = '{:.1f}'.format(surveyNumber / int(data[count][3]) * 100) + '%'
            data[count][6] = '{:.1f}'.format(int(data[count][6]) / surveyNumber)
            data[count][7] = '{:.1f}'.format(int(data[count][7]) / surveyNumber)

            to_render['data'] = data

        return render(request, 'afterSurvey.html', to_render)