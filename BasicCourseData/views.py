from django.shortcuts import render
from datetime import datetime, timedelta
from BasicCourseData.models import ResultDB
from django.db import DatabaseError
from use_function import getChooseDate, namedtuplefetchall
from django.db import connections


# Create your views here.
def basic_course_data_view(request):
    request.encoding = 'utf-8'

    if request.method == 'GET':
        # 存放最後回傳的資料
        # 資料庫最後更新日期
        finalUpdate = None
        data = []
        to_render = {}

        with connections['ResultDB'].cursor() as cursor:
            cursor.execute("select max(統計日期) as finalUpdate from course_total_data_v2")
            result = namedtuplefetchall(cursor)

            finalUpdate = result[0].finalUpdate

            cursor.execute("select * from course_total_data_v2 where 統計日期 = %s", [finalUpdate])
            result = namedtuplefetchall(cursor)

            maxRS = len(result)
            i = 0
            list_ = []

            for rs in result:
                data.clear()
                data.append(rs.課程代碼)
                data.append(rs.course_id)
                data.append(rs.course_name)
                data.append(rs.註冊人數_台灣)
                data.append(rs.註冊人數_非台灣)
                data.append(rs.熱門參與度)
                data.append(rs.退選人數)
                list_.append(data[:])

            # 回傳要呈現的資料
            to_render['result'] = list_

            # 預設日期範圍的下拉式選單，預設值為1:-請選擇-
            to_render['select'] = 1

            # 預設開課中、即將開課等等選項，預設值為3：所有課程
            to_render['optradio'] = 1

            # 僅提供給DownloadServlet使用，若使用者未設定開課日期的值，
            # 直接透過網址傳到DownloadServlet會有錯誤 所以若未設定開課日期，將其值設定為no
            to_render['selectStartDate_forDownload'] = 'no'

            # 最後更新
            to_render['finalUpdate'] = '最後資料更新時間 : ' + finalUpdate

            # 僅提供給DownloadServlet使用，將日期格式中的橫線去除
            for_download = datetime.strptime(finalUpdate, '%Y-%m-%d')
            to_render['finalUpdate_forDownload'] = for_download.strftime('%Y%m%d')

        return render(request, '1_BasicCourseData.html', to_render)

    if request.method == 'POST':
        # 存後最後輸出的資料，過濾所有條件
        list_ = []
        to_render = {}

        # 資料庫最後更新時間
        finalUpdate = None

        # 經由判斷後取得的使用者選擇的開課日期，從介面中的開課日期及日期範圍的值取得
        D_userChooseStartDate = None

        # 日期範圍
        select = request.POST.get('select', None)

        # 開課日期
        S_startDate = request.POST.get('startDate', None)

        # radio： 開課中、即將開課、已結束、全部課程，之後簡稱為radio
        optradio = request.POST.get('optradio', None)

        # 開課日期相關的資料庫語法
        date_ = None

        # 當日期範圍值不是1(-請選擇-)或開課日期不是空字串，代表使用者有使用日期的搜尋
        if select != '1' or S_startDate != '':
            # 將值傳入function取得資料庫語法需要的值，因為開課日期跟日期範圍，其實意義相同，只是設定方式不同
            D_userChooseStartDate = getChooseDate(select, S_startDate)

            # 若日期範圍的值是1(-請選擇-)，代表使用者選擇的日期條件是開課日期，這兩個條件一定是二選一的，不可能共存
            if select == '1':
                # 設定值為1，為了回傳到html後使用者所輸入的值不會被初始化
                to_render['select'] = 1
                to_render['selectStartDate'] = S_startDate

                # 僅提供給DownloadServlet，因為DownloadServlet是透過網址，取得介面上的值較為麻煩，所以在此設定
                for_download = datetime.strptime(S_startDate, '%Y-%m-%d')
                to_render['selectStartDate_forDownload'] = for_download.strftime('%Y%m%d')
            else:
                to_render['select'] = select
                to_render['selectStartDate'] = '年/月/日'
                to_render['selectStartDate_forDownload'] = 'no'

            date_ = D_userChooseStartDate

        # 進入else代表使用者沒有使用日期搜尋
        else:
            date_ = ''
            to_render['select'] = 1
            to_render['selectStartDate'] = '年/月/日'
            to_render['selectStartDate_forDownload'] = 'no'

        # 若使用者選擇已結束或是即將開課，即將日期語法清除，因為已結束或即將開課都不適用日期搜尋
        if (optradio=='2') or (optradio=='3'):
            date_ = ''
            to_render['select'] = 1
            to_render['selectStartDate'] = '年/月/日'
            to_render['selectStartDate_forDownload'] = 'no'

        now = datetime.today().strftime('%Y-%m-%d')
        to_render['optradio'] = optradio

        with connections['ResultDB'].cursor() as cursor:
            # 取得統計日期，方式是取得最後一筆資料，此筆資料的統計日期就是最新日期
            cursor.execute(
                "select * from course_total_data_v2 "
            )
            result = namedtuplefetchall(cursor)

            for rs in result:
                finalUpdate = rs.統計日期

            # 依據使用者選擇的條件，取得資料
            if date_ == '':
                if optradio == '0':
                    cursor.execute(
                        "select * from course_total_data_v2 "
                        "where 統計日期 = %s "
                        "AND (start_date < %s AND (end_date > %s OR end_date = 'NA'))",
                        [finalUpdate, now, now]
                    )
                    result = namedtuplefetchall(cursor)

                elif optradio == '1':
                    cursor.execute(
                        "select * from course_total_data_v2 "
                        "where 統計日期 = %s",
                        [finalUpdate]
                    )
                    result = namedtuplefetchall(cursor)

                elif optradio == '2':
                    cursor.execute(
                        "select * from course_total_data_v2 "
                        "where 統計日期 = %s "
                        "AND (start_date > %s AND start_date != '2030-01-01')",
                        [finalUpdate, now]
                    )
                    result = namedtuplefetchall(cursor)

                elif optradio == '3':
                    cursor.execute(
                        "select * from course_total_data_v2 "
                        "where 統計日期 = %s "
                        "AND (start_date < %s AND end_date < %s)",
                        [finalUpdate, now, now]
                    )
                    result = namedtuplefetchall(cursor)

            else:
                if optradio == '0':
                    cursor.execute(
                        "select * from course_total_data_v2 "
                        "where 統計日期 = %s "
                        "AND start_date > %s "
                        "AND (start_date < %s AND (end_date > %s OR end_date = 'NA'))",
                        [finalUpdate, date_, now, now]
                    )
                    result = namedtuplefetchall(cursor)

                elif optradio == '1':
                    cursor.execute(
                        "select * from course_total_data_v2 "
                        "where 統計日期 = %s "
                        "AND start_date > %s ",
                        [finalUpdate, date_]
                    )
                    result = namedtuplefetchall(cursor)

                elif optradio == '2':
                    cursor.execute(
                        "select * from course_total_data_v2 "
                        "where 統計日期 = %s "
                        "AND (start_date > %s AND start_date != '2030-01-01')",
                        [finalUpdate, now]
                    )
                    result = namedtuplefetchall(cursor)

                elif optradio == '3':
                    cursor.execute(
                        "select * from course_total_data_v2 "
                        "where 統計日期 = %s "
                        "AND (start_date < %s AND end_date < %s) ",
                        [finalUpdate, now, now]
                    )
                    result = namedtuplefetchall(cursor)

            # -------------------------------------

            # 依據使用者選擇的日期，取得資料
            data = []
            for rs in result:
                data.clear()
                data.append(rs.課程代碼)
                data.append(rs.course_id)
                data.append(rs.course_name)
                data.append(rs.註冊人數_台灣)
                data.append(rs.註冊人數_非台灣)
                data.append(rs.熱門參與度)
                data.append(rs.退選人數)
                list_.append(data[:])

            to_render['result'] = list_
            to_render['finalUpdate'] = '最後資料更新時間 : ' + finalUpdate

            for_download = datetime.strptime(finalUpdate, '%Y-%m-%d')
            to_render['finalUpdate_forDownload'] = for_download.strftime('%Y%m%d')

        return render(request, '1_BasicCourseData.html', to_render)

