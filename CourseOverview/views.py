from django.shortcuts import render
from use_function import getListAvg, namedtuplefetchall
from django.db import connections


# Create your views here.
def course_overview_view(request):
    request.encoding = 'utf-8'

    if request.method == 'GET':
        to_render = {}
        with connections['ResultDB'].cursor() as cursor:
            # 取得統計日期，方式是取得最後一筆資料，此筆資料的統計日期就是最新日期
            cursor.execute(
                "select * from course_total_data_v2 "
            )
            result = namedtuplefetchall(cursor)

            finalUpdate = str(result[-1].統計日期)

            # 取得同課程簡碼所在資料表 取出所有同課程簡碼
            state = False
            cursor.execute(
                "SELECT * "
                "FROM edxresult.course_total_data_v2 "
                "WHERE 統計日期=(select max(統計日期) from edxresult.course_total_data_v2)"
            )
            result = namedtuplefetchall(cursor)

            maxTotalList = len(result)

            cursor.execute(
                "SELECT * FROM edxresult.course_sameCourse_checklist WHERE course_id IS NOT null"
            )
            result = namedtuplefetchall(cursor)

            maxRS = len(result)

            data = [['' for i in range(maxRS)] for i in range(maxRS)]
            step = 0
            i = 0
            Total_Class = 0  # 課程數目最大
            for rs in result:
                temp = rs.同課程簡碼

                for step in range(i+1):
                    if temp == data[step][0]:
                        state = True
                        break

                if state is False:
                    data[i][0] = rs.同課程簡碼
                    i = i+1

                state = False
                Total_Class += 1

            SameClass = i  # 同課程最大數
            to_render['finalUpdate'] = '最後資料更新時間 : ' + finalUpdate
            i = 0

            # 取得同課程簡碼所在資料表 將課程加入到有相同的同課程簡碼裡
            temp_list = [['' for j in range(8)] for j in range(maxTotalList)]
            for rs in result:
                for step in range(SameClass):
                    if rs.同課程簡碼 == data[step][0]:
                        state = True
                        break

                if state is True:
                    for i in range(Total_Class):
                        if data[step][i] is '':
                            data[step][i] = rs.課程簡碼
                            break

                state = False

            cursor.execute(
                "SELECT * "
                "FROM edxresult.course_total_data_v2 "
                "WHERE 統計日期=(select max(統計日期) from edxresult.course_total_data_v2)"
            )
            result = namedtuplefetchall(cursor)

            i = 0
            for rs in result:
                temp_list[i][0] = rs.課程代碼
                temp_list[i][1] = rs.course_id
                temp_list[i][2] = rs.course_name
                temp_list[i][3] = rs.註冊人數_台灣
                temp_list[i][4] = rs.註冊人數_非台灣
                temp_list[i][5] = rs.熱門參與度
                temp_list[i][6] = rs.退選人數
                i = i+1

            z = 1
            temp_number = [0 for i in range(4)]
            data_sum = [['' for i in range(8)] for i in range(SameClass)]

            for i in range(SameClass):
                first = 0
                z = 1
                for j in range(maxTotalList):
                    if data[i][0] == 'E27G':
                        pass
                    if data[i][z] is not '':
                        if data[i][z] == temp_list[j][0]:
                            if first == 0:
                                data_sum[i][0] = temp_list[j][0]
                                data_sum[i][1] = temp_list[j][1]
                                data_sum[i][2] = temp_list[j][2]
                                data_sum[i][7] = data[i][0]
                                first = 1

                            temp_list[j][7] = data[i][0]
                            temp_number[0] += temp_list[j][3]
                            temp_list[j][3] = '{:,.2f}'.format(float(temp_list[j][3]))

                            temp_number[1] += temp_list[j][4]

                            temp_number[2] += temp_list[j][5]
                            temp_list[j][5] = '{:,.2f}'.format(float(temp_list[j][5]))

                            temp_number[3] += temp_list[j][6]
                            z += 1

                    elif data[i][z] is '':
                        data_sum[i][3] = '{:,}'.format(temp_number[0])
                        data_sum[i][4] = str(temp_number[1])
                        data_sum[i][5] = '{:,.2f}'.format(temp_number[2])
                        data_sum[i][6] = str(temp_number[3])

                        temp_number[0] = 0
                        temp_number[1] = 0
                        temp_number[2] = 0
                        temp_number[3] = 0
                        break

                    if j == (maxTotalList-1):
                        data_sum[i][3] = '{:,}'.format(temp_number[0])
                        data_sum[i][4] = str(temp_number[1])
                        data_sum[i][5] = '{:,.2f}'.format(temp_number[2])
                        data_sum[i][6] = str(temp_number[3])

                        temp_number[0] = 0
                        temp_number[1] = 0
                        temp_number[2] = 0
                        temp_number[3] = 0

            # 回傳課程代碼
            to_render['result'] = data
            # 回傳課程內容
            to_render['result_list'] = temp_list
            # 回傳合計欄位
            to_render['result_sum'] = data_sum
            # 相同課程簡碼的總數
            to_render['SameClass'] = SameClass
            # 課程簡碼的總數
            to_render['TotalClass'] = Total_Class
            to_render['temp_list_total'] = maxTotalList
            # 最後更新
            to_render['finalUpdate'] = '最後資料更新時間 : ' + finalUpdate

        return render(request, 'CourseOverview.html', to_render)





