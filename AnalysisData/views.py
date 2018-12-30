from django.shortcuts import render
from use_function import namedtuplefetchall, getBoxPlotValue, standardization, getListAvg
from use_function import CorrelationCoefficient, standardizationForCorrelationCoefficient, DecimalEncoder
from django.db import DatabaseError, connections
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import math
import json
import pandas as pd


# Create your views here.
def analysis_data_view(request):
    request.encoding = 'utf-8'
    request.GET = request.GET.copy()
    request.POST = request.POST.copy()
    to_render = {}

    if request.method == 'GET':
        select = request.GET.get('select', 2)
        select_int = int(select)
        to_render['select'] = select
        wc4sb = [['%SE%', '%SD%'], ['%SE%', '%SD%', '%X%']]
        statisticsBy = [" and (課程代碼  like '%%SE%%' or 課程代碼  like '%%SD%%' )",
                        " and 課程代碼  not like '%%SE%%' and 課程代碼 not like '%%SD%%' and 課程代碼 not like '%%X%%'",
                        " "]

        # 取得兩個月前的日期
        now = datetime.now()
        twoMonthAgo = (now + relativedelta(months=-2)).strftime('%Y-%m-%d')

        with connections['OpenEduDB'].cursor() as cursor:
            '''____________________年度____________________'''
            getYear = 0  # 每筆資料的年份

            # -----------------註冊人數------------------
            cursor.execute("SELECT date_joined FROM auth_user order by date_joined")
            result = namedtuplefetchall(cursor)

            # 取得最大年分
            MaxYear = datetime.strptime(str(result[-1].date_joined), '%Y-%m-%d %H:%M:%S').year

            # 創建列表並初始化
            registeredYear = [0 for i in range(int(MaxYear) - 2014 + 1)]

            # 最後回傳
            Json_registeredYear = []

            # 加入欄位定義
            jsonArray_temp = ["Element", "註冊人數"]
            jsonObject = {'role': 'style'}
            jsonArray_temp.append(jsonObject.copy())
            Json_registeredYear.append(jsonArray_temp.copy())

            # 計算資料
            for rs in result:
                getYear = datetime.strptime(str(rs.date_joined), '%Y-%m-%d %H:%M:%S').year
                registeredYear[getYear-2014] = registeredYear[getYear-2014] + 1

            # 加入JSON
            for i in range(len(registeredYear)):
                jsonArray_temp.clear()
                jsonArray_temp.append(str(i+2014))
                jsonArray_temp.append(registeredYear[i])
                jsonArray_temp.append('50a4e5')
                Json_registeredYear.append(jsonArray_temp.copy())

            to_render['Json_registeredYear'] = json.dumps(Json_registeredYear)
            # =============================================

            # --------------------性別---------------------
            Json_genderYear = []  # 最後回傳
            maleYear = [0 for i in range(int(MaxYear) - 2014 + 1)]  # 儲存男性數量
            femaleYear = [0 for i in range(int(MaxYear) - 2014 + 1)]  # 儲存女性數量
            otherYear = [0 for i in range(int(MaxYear) - 2014 + 1)]  # 儲存其他性別數量

            # 計算女性資料, edxapp.auth_user, auth_userprofile
            cursor.execute(
                "SELECT gender,date_joined "
                "FROM auth_user as AU, auth_userprofile as AUP "
                "WHERE AU.id = AUP.user_id and gender = 'f'"
            )
            result = namedtuplefetchall(cursor)

            for rs in result:
                getYear = datetime.strptime(str(rs.date_joined), '%Y-%m-%d %H:%M:%S').year
                femaleYear[getYear-2014] = femaleYear[getYear-2014] + 1

            # 計算男性資料, edxapp.auth_user, auth_userprofile
            cursor.execute(
                "SELECT gender,date_joined "
                "FROM auth_user as AU, auth_userprofile as AUP "
                "WHERE AU.id = AUP.user_id and gender = 'm'"
            )
            result = namedtuplefetchall(cursor)

            for rs in result:
                getYear = datetime.strptime(str(rs.date_joined), '%Y-%m-%d %H:%M:%S').year
                maleYear[getYear-2014] = maleYear[getYear-2014] + 1

            # 計算其他性別資料
            cursor.execute(
                "SELECT gender,date_joined "
                "FROM auth_user as AU, auth_userprofile as AUP "
                "WHERE AU.id = AUP.user_id and gender != 'f' and gender != 'm'"
            )
            result = namedtuplefetchall(cursor)

            for rs in result:
                getYear = datetime.strptime(str(rs.date_joined), '%Y-%m-%d %H:%M:%S').year
                otherYear[getYear-2014] = otherYear[getYear-2014] + 1

            # 加入欄位定義
            jsonArray_temp.clear()
            jsonArray_temp.append(' ')
            jsonArray_temp.append('男性')
            jsonArray_temp.append('女性')
            jsonArray_temp.append('其他')
            jsonObject = {'role': 'annotation'}
            jsonArray_temp.append(jsonObject.copy())
            Json_genderYear.append(jsonArray_temp.copy())

            # 加入JSON
            for i in range(len(registeredYear)):
                jsonArray_temp.clear()
                jsonArray_temp.append(str(2014+i))
                jsonArray_temp.append(maleYear[i])
                jsonArray_temp.append(femaleYear[i])
                jsonArray_temp.append(otherYear[i])
                jsonArray_temp.append(' ')
                Json_genderYear.append(jsonArray_temp.copy())

            to_render['Json_genderYear'] = json.dumps(Json_genderYear)

            '''___________________分布___________________'''

            # --------------------學歷---------------------
            education_p = 0  # 博士
            education_m = 0  # 碩士
            education_b = 0  # 學士
            education_a = 0  # 副學士
            education_hs = 0  # 高中
            education_jhs = 0  # 國中
            education_el = 0  # 國小
            education_other = 0  # 其他

            cursor.execute("SELECT id,level_of_education FROM auth_userprofile")
            result = namedtuplefetchall(cursor)

            for rs in result:
                if rs.level_of_education is not None:
                    if rs.level_of_education == 'p':
                        education_p = education_p + 1
                    elif rs.level_of_education ==  'm':
                        education_m = education_m + 1
                    elif rs.level_of_education == 'jhs':
                        education_jhs = education_jhs +1
                    elif rs.level_of_education == 'hs':
                        education_hs = education_hs + 1
                    elif rs.level_of_education == 'el':
                        education_el = education_el + 1
                    elif rs.level_of_education == 'b':
                        education_b = education_b +1
                    elif rs.level_of_education == 'a':
                        education_a = education_a + 1
                    else:
                        education_other = education_other + 1
                else:
                    education_other = education_other + 1

            to_render['education_p'] = education_p
            to_render['education_m'] = education_m
            to_render['education_jhs'] = education_jhs
            to_render['education_hs'] = education_hs
            to_render['education_el'] = education_el
            to_render['education_b'] = education_b
            to_render['education_a'] = education_a
            to_render['education_other'] = education_other
            # ===============================================

            # --------------------年齡-----------------------
            age = [0, 0, 0, 0, 0, 0, 0, 0]
            cursor.execute("SELECT year_of_birth FROM auth_userprofile")
            result = namedtuplefetchall(cursor)

            for rs in result:
                year_of_birth = rs.year_of_birth
                if year_of_birth is None:
                    year_of_birth = 0

                index = (int(MaxYear) - int(year_of_birth)) / 4 - 3
                if 0 <= index <= 6:
                    age[int(index)] = age[int(index)] + 1
                elif 6 < index < 20:
                    age[6] = age[6] + 1
                elif index == -1:
                    age[0] = age[0] + 1
                else:
                    age[7] = age[7] + 1
            to_render['age'] = age

            # 性別
            gender = [0, 0, 0]
            for i in range(int(MaxYear) - 2014 + 1):
                gender[0] = gender[0] + maleYear[i]
                gender[1] = gender[1] + femaleYear[i]
                gender[2] = gender[2] + otherYear[i]
            to_render['gender'] = gender

        with connections['ResultDB'].cursor() as cursor:
            # course_total_data_v2 更新日期
            cursor.execute("SELECT max(統計日期) as date FROM course_total_data_v2")
            result = namedtuplefetchall(cursor)

            update_course_total_data = result[-1].date
            to_render['update_course_total_data'] = update_course_total_data

            # 取得年份
            MaxYear = datetime.strptime(update_course_total_data, '%Y-%m-%d').year
            minYear = 2014
            currentYear = minYear

            '''___________________年度___________________'''

            # -----------------開課週數------------------
            Json_DurationWeekYear = []
            Json_DurationWeekYear_RE = []
            data = []
            boxPlotData = []
            jsonArray_temp = []
            jsonObject = {}
            while currentYear <= int(MaxYear):
                data.clear()
                boxPlotData.clear()
                wildcard = '%X%'
                cursor.execute(
                    "SELECT  duration_week "
                    "FROM course_total_data_v2 "
                    "WHERE 統計日期 = %s and start_date > %s and start_date < %s "
                    "and duration_week is not NULL and 課程代碼 not like '%%X%%'",
                    [update_course_total_data, str(currentYear), str(currentYear+1)]
                )
                result = namedtuplefetchall(cursor)

                for rs in result:
                    data.append(rs.duration_week)

                # 一般
                boxPlotData = getBoxPlotValue(data)
                jsonArray_temp.clear()
                jsonObject.clear()
                jsonObject['exp'] = currentYear
                jsonObject['high'] = boxPlotData[0]
                jsonObject['open'] = boxPlotData[1]
                jsonObject['mid'] = boxPlotData[2]
                jsonObject['close'] = boxPlotData[3]
                jsonObject['low'] = boxPlotData[4]
                Json_DurationWeekYear.append(jsonObject.copy())

                # 標準化
                data = standardization(data)
                boxPlotData = getBoxPlotValue(data)
                jsonObject.clear()
                jsonObject['exp'] = currentYear
                jsonObject['high'] = boxPlotData[0]
                jsonObject['open'] = boxPlotData[1]
                jsonObject['mid'] = boxPlotData[2]
                jsonObject['close'] = boxPlotData[3]
                jsonObject['low'] = boxPlotData[4]
                Json_DurationWeekYear_RE.append(jsonObject.copy())

                currentYear = currentYear + 1

            to_render['Json_DurationWeekYear'] = json.dumps(Json_DurationWeekYear)
            to_render['Json_DurationWeekYear_RE'] = json.dumps(Json_DurationWeekYear_RE)

            # 影片數量、討論區討論次數、作答過半人數比例、觀看過半人數比例、退選率
            Json_NumberOfMovieYear = []  # 影片數量
            Json_NumberOfDiscussionsYear = []  # 討論區討論次數
            Json_AnswerHalfYear = []  # 作答過半人數比例
            Json_WatchHalfYear = []  # 觀看過半人數比例
            Json_DropYear = []  # 退選率
            Json_RegisterCourseYear = []  # 註冊課程人次

            Json_NumberOfMovieYear_RE = []  # 影片數量_標準化
            Json_NumberOfDiscussionsYear_RE = []  # 討論區討論次數_標準化
            Json_AnswerHalfYear_RE = []  # 作答過半人數比例_標準化
            Json_WatchHalfYear_RE = []  # 觀看過半人數比例_標準化
            Json_DropYear_RE = []  # 退選率_標準化
            Json_RegisterCourseYear_RE = []  # 註冊課程人次_標準化

            NumberOfMovieYear = []
            NumberOfDiscussionsYear = []
            AnswerHalfYear = []
            WatchHalfYear = []
            DropYear = []
            RegisterCourseYear = []

            haveData = False
            currentYear = minYear
            while currentYear <= int(MaxYear):
                boxPlotData.clear()
                NumberOfMovieYear.clear()
                NumberOfDiscussionsYear.clear()
                AnswerHalfYear.clear()
                WatchHalfYear.clear()
                DropYear.clear()
                RegisterCourseYear.clear()

                cursor.execute(
                    "SELECT 課程影片數目 as NumberOfMovie, 討論區討論次數  as NumberOfDiscussions, "
                    "作答過半人數/註冊人數 as AnswerHalf, "
                    "(影片觀看過半人數_台灣 + 影片觀看過半人數_非台灣)/(影片觀看人數_非台灣 + 影片觀看人數台灣) as WatchHalf, "
                    "退選人數/註冊人數 as droppercent, 註冊人數 as RegisterCourse "
                    "FROM course_total_data_v2 "
                    "WHERE 統計日期 = %s and start_date > %s and start_date < %s " + statisticsBy[select_int],
                    [update_course_total_data, str(currentYear), str(currentYear + 1)]
                )
                result = namedtuplefetchall(cursor)

                for rs in result:
                    haveData = True
                    if rs.AnswerHalf is not None:
                        AnswerHalfYear.append(float(rs.AnswerHalf))
                    else:
                        AnswerHalfYear.append(0)

                    if rs.WatchHalf is not None:
                        WatchHalfYear.append(float(rs.WatchHalf))
                    else:
                        WatchHalfYear.append(0)

                    if rs.droppercent is not None:
                        DropYear.append(float(rs.droppercent))
                    else:
                        DropYear.append(0)

                    NumberOfMovieYear.append(rs.NumberOfMovie)
                    NumberOfDiscussionsYear.append(rs.NumberOfDiscussions)
                    # AnswerHalfYear.append(float(rs.AnswerHalf))
                    # WatchHalfYear.append(rs.WatchHalf)
                    # DropYear.append(rs.droppercent)
                    RegisterCourseYear.append(rs.RegisterCourse)

                if haveData:
                    # 加入影片數量資料
                    boxPlotData = getBoxPlotValue(NumberOfMovieYear)
                    jsonArray_temp.clear()
                    jsonObject.clear()
                    jsonObject['exp'] = currentYear
                    jsonObject['high'] = boxPlotData[0]
                    jsonObject['open'] = boxPlotData[1]
                    jsonObject['mid'] = boxPlotData[2]
                    jsonObject['close'] = boxPlotData[3]
                    jsonObject['low'] = boxPlotData[4]
                    Json_NumberOfMovieYear.append(jsonObject.copy())

                    # 加入討論區次數資料
                    boxPlotData = getBoxPlotValue(NumberOfDiscussionsYear)
                    jsonArray_temp.clear()
                    jsonObject.clear()
                    jsonObject['exp'] = currentYear
                    jsonObject['high'] = boxPlotData[0]
                    jsonObject['open'] = boxPlotData[1]
                    jsonObject['mid'] = boxPlotData[2]
                    jsonObject['close'] = boxPlotData[3]
                    jsonObject['low'] = boxPlotData[4]
                    Json_NumberOfDiscussionsYear.append(jsonObject.copy())

                    # 加入作答過半人數比例資料
                    boxPlotData = getBoxPlotValue(AnswerHalfYear)
                    jsonArray_temp.clear()
                    jsonObject.clear()
                    jsonObject['exp'] = currentYear
                    jsonObject['high'] = '{:,.2f}'.format(boxPlotData[0]*100)
                    jsonObject['open'] = '{:,.2f}'.format(boxPlotData[1]*100)
                    jsonObject['mid'] = '{:,.2f}'.format(boxPlotData[2]*100)
                    jsonObject['close'] = '{:,.2f}'.format(boxPlotData[3]*100)
                    jsonObject['low'] = '{:,.2f}'.format(boxPlotData[4]*100)
                    Json_AnswerHalfYear.append(jsonObject.copy())

                    # 加入觀看過半人數比例資料
                    boxPlotData = getBoxPlotValue(WatchHalfYear)
                    jsonArray_temp.clear()
                    jsonObject.clear()
                    jsonObject['exp'] = currentYear
                    jsonObject['high'] = '{:,.2f}'.format(boxPlotData[0] * 100)
                    jsonObject['open'] = '{:,.2f}'.format(boxPlotData[1] * 100)
                    jsonObject['mid'] = '{:,.2f}'.format(boxPlotData[2] * 100)
                    jsonObject['close'] = '{:,.2f}'.format(boxPlotData[3] * 100)
                    jsonObject['low'] = '{:,.2f}'.format(boxPlotData[4] * 100)
                    Json_WatchHalfYear.append(jsonObject.copy())

                    # 加入退選率資料
                    boxPlotData = getBoxPlotValue(DropYear)
                    jsonArray_temp.clear()
                    jsonObject.clear()
                    jsonObject['exp'] = currentYear
                    jsonObject['high'] = '{:,.2f}'.format(boxPlotData[0] * 100)
                    jsonObject['open'] = '{:,.2f}'.format(boxPlotData[1] * 100)
                    jsonObject['mid'] = '{:,.2f}'.format(boxPlotData[2] * 100)
                    jsonObject['close'] = '{:,.2f}'.format(boxPlotData[3] * 100)
                    jsonObject['low'] = '{:,.2f}'.format(boxPlotData[4] * 100)
                    Json_DropYear.append(jsonObject.copy())

                    # 加入註冊課程人次資料
                    boxPlotData = getBoxPlotValue(RegisterCourseYear)
                    jsonArray_temp.clear()
                    jsonObject.clear()
                    jsonObject['exp'] = currentYear
                    jsonObject['high'] = boxPlotData[0]
                    jsonObject['open'] = boxPlotData[1]
                    jsonObject['mid'] = boxPlotData[2]
                    jsonObject['close'] = boxPlotData[3]
                    jsonObject['low'] = boxPlotData[4]
                    Json_RegisterCourseYear.append(jsonObject.copy())

                    '''_____以下為標準化_____'''
                    # 加入影片數量資料
                    NumberOfMovieYear = standardization(NumberOfMovieYear)
                    boxPlotData = getBoxPlotValue(NumberOfMovieYear)
                    jsonArray_temp.clear()
                    jsonObject.clear()
                    jsonObject['exp'] = currentYear
                    jsonObject['high'] = boxPlotData[0]
                    jsonObject['open'] = boxPlotData[1]
                    jsonObject['mid'] = boxPlotData[2]
                    jsonObject['close'] = boxPlotData[3]
                    jsonObject['low'] = boxPlotData[4]
                    Json_NumberOfMovieYear_RE.append(jsonObject.copy())

                    # 加入討論區次數資料
                    NumberOfDiscussionsYear = standardization(NumberOfDiscussionsYear)
                    boxPlotData = getBoxPlotValue(NumberOfDiscussionsYear)
                    jsonArray_temp.clear()
                    jsonObject.clear()
                    jsonObject['exp'] = currentYear
                    jsonObject['high'] = boxPlotData[0]
                    jsonObject['open'] = boxPlotData[1]
                    jsonObject['mid'] = boxPlotData[2]
                    jsonObject['close'] = boxPlotData[3]
                    jsonObject['low'] = boxPlotData[4]
                    Json_NumberOfDiscussionsYear_RE.append(jsonObject.copy())

                    # 加入作答過半人數比例資料
                    AnswerHalfYear = standardization(AnswerHalfYear)
                    boxPlotData = getBoxPlotValue(AnswerHalfYear)
                    jsonArray_temp.clear()
                    jsonObject.clear()
                    jsonObject['exp'] = currentYear
                    jsonObject['high'] = '{:,.2f}'.format(boxPlotData[0] * 100)
                    jsonObject['open'] = '{:,.2f}'.format(boxPlotData[1] * 100)
                    jsonObject['mid'] = '{:,.2f}'.format(boxPlotData[2] * 100)
                    jsonObject['close'] = '{:,.2f}'.format(boxPlotData[3] * 100)
                    jsonObject['low'] = '{:,.2f}'.format(boxPlotData[4] * 100)
                    Json_AnswerHalfYear_RE.append(jsonObject.copy())

                    # 加入觀看過半人數比例資料
                    WatchHalfYear = standardization(WatchHalfYear)
                    boxPlotData = getBoxPlotValue(WatchHalfYear)
                    jsonArray_temp.clear()
                    jsonObject.clear()
                    jsonObject['exp'] = currentYear
                    jsonObject['high'] = '{:,.2f}'.format(boxPlotData[0] * 100)
                    jsonObject['open'] = '{:,.2f}'.format(boxPlotData[1] * 100)
                    jsonObject['mid'] = '{:,.2f}'.format(boxPlotData[2] * 100)
                    jsonObject['close'] = '{:,.2f}'.format(boxPlotData[3] * 100)
                    jsonObject['low'] = '{:,.2f}'.format(boxPlotData[4] * 100)
                    Json_WatchHalfYear_RE.append(jsonObject.copy())

                    # 加入退選率資料
                    DropYear = standardization(DropYear)
                    boxPlotData = getBoxPlotValue(DropYear)
                    jsonArray_temp.clear()
                    jsonObject.clear()
                    jsonObject['exp'] = currentYear
                    jsonObject['high'] = '{:,.2f}'.format(boxPlotData[0] * 100)
                    jsonObject['open'] = '{:,.2f}'.format(boxPlotData[1] * 100)
                    jsonObject['mid'] = '{:,.2f}'.format(boxPlotData[2] * 100)
                    jsonObject['close'] = '{:,.2f}'.format(boxPlotData[3] * 100)
                    jsonObject['low'] = '{:,.2f}'.format(boxPlotData[4] * 100)
                    Json_DropYear_RE.append(jsonObject.copy())

                    # 加入註冊課程人次資料
                    RegisterCourseYear = standardization(RegisterCourseYear)
                    boxPlotData = getBoxPlotValue(RegisterCourseYear)
                    jsonArray_temp.clear()
                    jsonObject.clear()
                    jsonObject['exp'] = currentYear
                    jsonObject['high'] = boxPlotData[0]
                    jsonObject['open'] = boxPlotData[1]
                    jsonObject['mid'] = boxPlotData[2]
                    jsonObject['close'] = boxPlotData[3]
                    jsonObject['low'] = boxPlotData[4]
                    Json_RegisterCourseYear_RE.append(jsonObject.copy())

                currentYear = currentYear + 1

            to_render['Json_NumberOfMovieYear'] = json.dumps(Json_NumberOfMovieYear)
            to_render['Json_NumberOfDiscussionsYear'] = json.dumps(Json_NumberOfDiscussionsYear)
            to_render['Json_AnswerHalfYear'] = json.dumps(Json_AnswerHalfYear)
            to_render['Json_WatchHalfYear'] = json.dumps(Json_WatchHalfYear)
            to_render['Json_DropYear'] = json.dumps(Json_DropYear)
            to_render['Json_RegisterCourseYear'] = json.dumps(Json_RegisterCourseYear)
            to_render['Json_NumberOfMovieYear_RE'] = json.dumps(Json_NumberOfMovieYear_RE)
            to_render['Json_NumberOfDiscussionsYear_RE'] = json.dumps(Json_NumberOfDiscussionsYear_RE)
            to_render['Json_AnswerHalfYear_RE'] = json.dumps(Json_AnswerHalfYear_RE)
            to_render['Json_WatchHalfYear_RE'] = json.dumps(Json_WatchHalfYear_RE)
            to_render['Json_DropYear_RE'] = json.dumps(Json_DropYear_RE)
            to_render['Json_RegisterCourseYear_RE'] = json.dumps(Json_RegisterCourseYear_RE)
            # ========================================================================

            Json_NumberOfCourseYear = []  # 開課數量
            NumberOfCourseYear_Self = [0 for i in range(int(MaxYear) - minYear + 1)]
            NumberOfCourseYear_Normal = [0 for i in range(int(MaxYear) - minYear + 1)]

            currentYear = minYear
            while currentYear <= int(MaxYear):
                cursor.execute(
                    "SELECT 課程代碼 "
                    "FROM course_total_data_v2 "
                    "WHERE 統計日期 = %s and start_date > %s and start_date < %s",
                    [update_course_total_data, str(currentYear), str(currentYear+1)]
                )
                result = namedtuplefetchall(cursor)

                for rs in result:
                    if rs.課程代碼[0] == 'S':
                        NumberOfCourseYear_Self[currentYear-2014] = NumberOfCourseYear_Self[currentYear-2014] + 1
                    else:
                        NumberOfCourseYear_Normal[currentYear-2014] = NumberOfCourseYear_Normal[currentYear-2014] + 1
                currentYear = currentYear + 1

            for i in range(int(MaxYear) - 2014 + 1):
                # 加入開課數量資料
                jsonArray_temp.clear()
                jsonObject.clear()
                jsonObject['year'] = str(2014+i)
                jsonObject['europe'] = NumberOfCourseYear_Self[i]
                jsonObject['namerica'] = NumberOfCourseYear_Normal[i]
                Json_NumberOfCourseYear.append(jsonObject.copy())
            to_render['Json_NumberOfCourseYear'] = json.dumps(Json_NumberOfCourseYear)
            # ================================================================

            '''_____分布圖-開課時間達兩個月以上課程_____'''

            # -------------影片平均長度(AML) & 影片觀看過半人數比例(WHP)--------------
            Json_AML_WHP = []
            avgMovieLong = []
            WatchHalfPercent = []

            # 設定欄位
            jsonArray_temp.clear()
            jsonArray_temp.append('影片平均長度')
            jsonArray_temp.append('影片觀看過半人數比例')
            Json_AML_WHP.append(jsonArray_temp.copy())

            cursor.execute(
                "SELECT 影片平均長度,(影片觀看過半人數_台灣 + 影片觀看過半人數_非台灣)/註冊人數 as percent "
                "FROM edxresult.course_total_data_v2 "
                "WHERE 統計日期 = %s and start_date < %s and 課程影片數目 != 0 and 影片平均長度 != 0 and 註冊人數 != 0"
                "" + statisticsBy[select_int], [update_course_total_data, twoMonthAgo]
            )
            result = namedtuplefetchall(cursor)

            for rs in result:
                avgMovieLong.append(float(rs.影片平均長度))
                WatchHalfPercent.append(float(rs.percent))
                jsonArray_temp.clear()
                jsonArray_temp.append(rs.影片平均長度)
                jsonArray_temp.append(rs.percent)
                Json_AML_WHP.append(jsonArray_temp.copy())

            avgAML = getListAvg(avgMovieLong)
            avgWHP = getListAvg(WatchHalfPercent)
            cc_AML_WHP_normal = CorrelationCoefficient(avgMovieLong, WatchHalfPercent, avgAML, avgWHP)
            degree_AML_WHP_normal = degree(cc_AML_WHP_normal)

            to_render['Json_AML_WHP'] = json.dumps(Json_AML_WHP, cls=DecimalEncoder)
            to_render['cc_AML_WHP_normal'] = '{:,.2f}'.format(cc_AML_WHP_normal)
            to_render['degree_AML_WHP_normal'] = degree_AML_WHP_normal
            to_render['avgAML'] = '{:,.2f}'.format(avgAML)
            to_render['avgWHP'] = '{:,.2f}'.format(avgWHP)

            '''_______以下為標準化_______'''
            Json_AML_WHP_RE = []
            AML_WHP_List_RE = standardizationForCorrelationCoefficient(WatchHalfPercent, avgMovieLong)
            avgMovieLong_RE = []
            WatchHalfPercent_RE = []

            # 設定欄位
            jsonArray_temp.clear()
            jsonArray_temp.append('影片平均長度')
            jsonArray_temp.append('影片觀看過半人數比例')
            Json_AML_WHP_RE.append(jsonArray_temp.copy())

            for i in range(len(AML_WHP_List_RE)):
                avgMovieLong_RE.append(AML_WHP_List_RE[i][1])
                WatchHalfPercent_RE.append(AML_WHP_List_RE[i][0])
                # 加入資料
                jsonArray_temp.clear()
                jsonArray_temp.append(AML_WHP_List_RE[i][1])
                jsonArray_temp.append(AML_WHP_List_RE[i][0])
                Json_AML_WHP_RE.append(jsonArray_temp.copy())

            avgAML_RE = getListAvg(avgMovieLong_RE)
            avgWHP_RE = getListAvg(WatchHalfPercent_RE)
            cc_AML_WHP_RE = CorrelationCoefficient(avgMovieLong_RE, WatchHalfPercent_RE, avgAML_RE, avgWHP_RE)
            degree_AML_WHP_RE = degree(cc_AML_WHP_RE)

            to_render['Json_AML_WHP_RE'] = json.dumps(Json_AML_WHP_RE, cls=DecimalEncoder)
            to_render['cc_AML_WHP_RE'] = '{:,.2f}'.format(cc_AML_WHP_RE)
            to_render['degree_AML_WHP_RE'] = degree_AML_WHP_RE
            to_render['avgAML_RE'] = '{:,.2f}'.format(avgAML_RE)
            to_render['avgWHP_RE'] = '{:,.2f}'.format(avgWHP_RE)
            # =================================================

            # ----------影片平均長度(AML) & 影片觀看人數比例(WP)----------
            Json_AML_WP = []
            WatchPercent = []

            # 設定欄位
            jsonArray_temp.clear()
            jsonArray_temp.append('影片平均長度')
            jsonArray_temp.append('影片觀看過半人數比例')
            Json_AML_WP.append(jsonArray_temp.copy())

            cursor.execute(
                "SELECT 影片平均長度,(影片觀看人數台灣 + 影片觀看人數_非台灣)/註冊人數 as percent "
                "FROM edxresult.course_total_data_v2  "
                "WHERE 統計日期 = %s and start_date < %s and 課程影片數目 != 0 and 影片平均長度 != 0 and 註冊人數 != 0"
                "" + statisticsBy[select_int], [update_course_total_data, twoMonthAgo]
            )
            result = namedtuplefetchall(cursor)

            for rs in result:
                WatchPercent.append(rs.percent)

                jsonArray_temp.clear()
                jsonArray_temp.append(rs.影片平均長度)
                jsonArray_temp.append(rs.percent)
                Json_AML_WP.append(jsonArray_temp.copy())

            avgWP = getListAvg(WatchPercent)
            cc_AML_WP_normal = CorrelationCoefficient(avgMovieLong, WatchPercent, avgAML, avgWP)
            degree_AML_WP_normal = degree(cc_AML_WP_normal)

            to_render['Json_AML_WP'] = json.dumps(Json_AML_WP, cls=DecimalEncoder)
            to_render['cc_AML_WP_normal'] = '{:,.2f}'.format(cc_AML_WP_normal)
            to_render['degree_AML_WP_normal'] = degree_AML_WP_normal
            to_render['avgWP'] = '{:,.2f}'.format(avgWP)

            '''_______以下為標準化_______'''
            Json_AML_WP_RE = []
            AML_WP_List_RE = standardizationForCorrelationCoefficient(WatchPercent, avgMovieLong)
            avgMovieLong_RE.clear()
            WatchPercent_RE = []

            # 設定欄位
            jsonArray_temp.clear()
            jsonArray_temp.append('影片平均長度')
            jsonArray_temp.append('影片觀看過半人數比例')
            Json_AML_WP_RE.append(jsonArray_temp.copy())

            for i in range(len(AML_WP_List_RE)):
                avgMovieLong_RE.append(AML_WP_List_RE[i][1])
                WatchPercent_RE.append(AML_WP_List_RE[i][0])
                # 加入資料
                jsonArray_temp.clear()
                jsonArray_temp.append(AML_WP_List_RE[i][1])
                jsonArray_temp.append(AML_WP_List_RE[i][0])
                Json_AML_WP_RE.append(jsonArray_temp.copy())

            avgAML_RE = getListAvg(avgMovieLong_RE)
            avgWP_RE = getListAvg(WatchPercent_RE)
            cc_AML_WP_RE = CorrelationCoefficient(avgMovieLong_RE, WatchPercent_RE, avgAML_RE, avgWP_RE)
            degree_AML_WP_RE = degree(cc_AML_WP_RE)

            to_render['Json_AML_WP_RE'] = json.dumps(Json_AML_WP_RE, cls=DecimalEncoder)
            to_render['cc_AML_WP_RE'] = '{:,.2f}'.format(cc_AML_WP_RE)
            to_render['degree_AML_WP_RE'] = degree_AML_WP_RE
            to_render['avgAML_RE'] = '{:,.2f}'.format(avgAML_RE)
            to_render['avgWP_RE'] = '{:,.2f}'.format(avgWHP_RE)

        return render(request, 'analysisData.html', to_render)


def calculate_education(data, avg_data):
    output = (data.博士 * 7 * (data.博士 / avg_data.avg_p)) + (data.碩士 * 6 * (data.碩士 / avg_data.avg_m)) + \
             (data.學士 * 5 * (data.學士 / avg_data.avg_b)) + (data.副學士 * 4 * (data.副學士 / avg_data.avg_a)) + \
             (data.高中 * 3 * (data.高中 / avg_data.avg_hs)) + (data.國中 * 2 * (data.國中 / avg_data.avg_jhs)) + \
             (data.國小 * 1 * (data.國小 / avg_data.avg_el)) * (data.total / avg_data.avg_all)
    return output


def Correlation_X(x, y, avg_x, avg_y):
    Correlation_x = 0
    Correlation_x = Correlation_x + ((x - avg_x) * (y - avg_y))
    return Correlation_x


def preStandard(x, avg_x):
    return (x - avg_x) * (x - avg_x)


def Correlation(x, y, z):
    return x / (math.sqrt(y) * math.sqrt(z))


def degree(x):
    if x > 0.7:
        return '高度正相關'
    elif x >= 0.3:
        return '中度正相關'
    elif x >= 0:
        return '低度正相關'
    elif x <= -0.7:
        return '高度負相關'
    elif x <= -0.3:
        return '中度負相關'
    else:
        return '低度負相關'






