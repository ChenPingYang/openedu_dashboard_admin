from django.shortcuts import render
from GlossaryObject import GlossaryObject
from DefinitionString import DefinitionString


# Create your views here.
def glossary_view(request):
    request.encoding = 'utf-8'
    to_render = {}


    '''
    request.GET = request.GET.copy()
    request.POST = request.POST.copy()
    
    if request.method == 'GET':
        # 宣告儲存定義的物件
        
        f = DefinitionString()
        gList = f.getGlossaryList()
        id_string = request.GET['id']
        request.GET['id'] = id_string
        id_int = int(id_string)

        # 儲存選項
        option = []

        # 將id的內容回傳
        request.GET['name'] = gList[id_int].name
        request.GET['definition'] = gList[id_int].definition
        if gList[id_int].calculation is None:
            request.GET['haveCalculation'] = False
        else:
            request.GET['calculation'] = gList[id_int].calculation
            request.GET['haveCalculation'] = True

        # 將選項回傳
        for i in range(len(gList)):
            data = [str(gList[i].id_), '{:0>3d}'.format(gList[i].id_) + ' # ' + gList[i].name]
            option.append(data[:])

        request.GET['option'] = option

        return render(request, 'glossaryV2.html', locals())
    '''
    return render(request, 'glossaryV2.html', to_render)

