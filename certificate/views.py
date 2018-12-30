from django.shortcuts import render
from django.db import DatabaseError, connections
from use_function import namedtuplefetchall
from datetime import datetime
from dateutil.relativedelta import relativedelta
import json


# Create your views here.
def certificate_view(request):
    request.encoding = 'utf-8'
    request.GET = request.GET.copy()
    request.POST = request.POST.copy()
    to_render = {}

    if request.method == 'GET':
        jsonObject = {}
        jsonArray_temp = []
        avg_watch = [0 for i in range(5)]
        avg_realWatch = [0 for i in range(5)]
        with connections['ResultDB'].cursor() as cursor:
            # 顯示資料
            cursor.execute("SELECT max(統計日期) as max_update FROM course_total_data_v2")
            result = namedtuplefetchall(cursor)

            maxUpdate = None
            if len(result) != 0:
                maxUpdate = result[-1].max_update

            cursor.execute("SELECT max(run_date) as max_run_date FROM student_total_data0912")
            result = namedtuplefetchall(cursor)

            maxRunDate = None
            if len(result) != 0:
                maxRunDate = result[-1].max_run_date

            cursor.execute("SELECT sum(證書人數) as sum_pass "
                           "FROM course_total_data_v2  WHERE"
                           " 統計日期 = %s", [maxUpdate])
            result = namedtuplefetchall(cursor)

            sumPassPeople = 0
            if len(result) != 0:
                sumPassPeople = result[-1].sum_pass

            cursor.execute("SELECT 證書人數,course_name "
                           "FROM course_total_data_v2 "
                           "WHERE 統計日期 = %s order by 證書人數  desc limit 0, 5", [maxUpdate])
            result = namedtuplefetchall(cursor)

            for rs in result:
                course_name = rs.course_name
                certificate = rs.證書人數

                jsonObject.clear()
                jsonObject['courseName'] = course_name
                jsonObject['value'] = certificate
                jsonArray_temp.append(jsonObject.copy())

            cursor.execute(
                "SELECT 證書人數,course_name,課程代碼  "
                "FROM course_total_data_v2 "
                "WHERE 證書人數>0 and 統計日期 = %s order by 證書人數  desc", [maxUpdate]
            )
            result = namedtuplefetchall(cursor)

            jsonArray_temp_1 = []
            jsonArray_table = []
            for rs in result:
                course_name = rs.course_name
                course_id = rs.課程代碼
                certificate = rs.證書人數

                jsonArray_temp_1.clear()
                jsonArray_temp_1.append(course_name)
                jsonArray_temp_1.append("ChartDataServlet?mode=2&course=" + course_id)
                jsonArray_temp_1.append(certificate)
                jsonArray_table.append(jsonArray_temp_1[:])

            # 平均開課週數
            cursor.execute(
                "SELECT user_id, count(c_table.course_id) as count_cid, name "
                "FROM student_total_data0912 as c_table inner join course_total_data_v2 as s_table on (c_table.course_id=s_table.course_id) "
                "WHERE 統計日期= %s and run_date= %s group by user_id ,name order by count(c_table.course_id) desc limit 0,100",
                [maxUpdate, maxRunDate]
            )
            result = namedtuplefetchall(cursor)

            jsonArray_course = []
            user_id = ''
            for rs in result:
                # 判斷是否該名字是中文，如果是的話以'*'字號來消音保護隱私
                if len(rs.name.encode()) != len(rs.name):
                    name = rs.name[0:1] + '*' + rs.name[2:]
                else:
                    name = rs.name

                countCourse = rs.count_cid
                user_id = str(rs.user_id)

                jsonArray_temp_1.clear()
                jsonArray_temp_1.append(name)
                jsonArray_temp_1.append("studentInfoServlet?userId=" + user_id)
                jsonArray_temp_1.append(countCourse)
                jsonArray_course.append(jsonArray_temp_1[:])

            cursor.execute(
                "SELECT count(user_id) as count_pass,user_id,name "
                "FROM edxresult.student_total_data0912 "
                "WHERE certificate=1 group by user_id,name order by count(user_id) desc limit 0,100"
            )
            result = namedtuplefetchall(cursor)

            jsonArray_pass = []
            for rs in result:
                # 判斷是否該名字是中文，如果是的話以'*'字號來消音保護隱私
                if len(rs.name.encode()) != len(rs.name):
                    name = rs.name[0:1] + '*' + rs.name[2:]
                else:
                    name = rs.name

                user_id = str(rs.user_id)
                passCount = rs.count_pass
                jsonArray_temp_1.clear()
                jsonArray_temp_1.append(name)
                jsonArray_temp_1.append("studentInfoServlet?userId=" + user_id)
                jsonArray_temp_1.append(passCount)
                jsonArray_pass.append(jsonArray_temp_1[:])

            now = datetime.now()
            time_start = (now + relativedelta(years=-3))
            time_end = (now + relativedelta(years=-2))
            now = (now + relativedelta(years=-3))

            count = 0
            recentYearDuration = [0 for i in range(5)]
            count_watch = [0 for i in range(5)]
            while count < 5:
                Standard_Deviation = 0
                countMember = 0

                cursor.execute(
                    "SELECT sum(證書人數) as sum_c "
                    "FROM edxresult.course_total_data_v2 "
                    "WHERE start_date < %s and start_date > %s and 統計日期 = %s",
                    [time_end.strftime('%Y-01-01'), time_start.strftime('%Y-01-01'), maxUpdate]
                )
                result = namedtuplefetchall(cursor)

                if len(result) != 0:
                    recentYearDuration[count] = now.year
                    count_watch[count] = result[-1].sum_c

                count = count + 1
                now = now + relativedelta(years=1)
                time_start = time_start + relativedelta(years=1)
                time_end = time_end + relativedelta(years=1)

            to_render['sumPassPeople'] = sumPassPeople
            to_render['jsonArray_temp'] = json.dumps(jsonArray_temp)
            to_render['jsonArray_table'] = json.dumps(jsonArray_table)
            to_render['recentYearDuration'] = recentYearDuration
            to_render['count_watch'] = count_watch
            to_render['avg_watch'] = avg_watch
            to_render['avg_realWatch'] = avg_realWatch
            to_render['user_id'] = user_id
            to_render['jsonArray_pass'] = json.dumps(jsonArray_pass)
            to_render['jsonArray_course'] = json.dumps(jsonArray_course)

        return render(request, 'certificate.html', to_render)



