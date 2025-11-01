import math
import pandas as pd
from io import BytesIO
from django.http import HttpResponse


def paginate_query_set_list(query_set, params, serializer, context=None, data_key='data'): 
    '''
        this function make the pagination with it self 
        u give it the query and serializer class and filter and it runs all of this and return obj of result
    '''
    page            = to_int(params.get('page'), 1)
    size            = to_int(params.get('size'), 10)
    
    
    count           = query_set.count()
    instances       = query_set[(page-1)*size : (page) * size]

    return {
        data_key        : serializer(instances, many=True, context=context).data,
        'total_pages'   : math.ceil(count/size) or 1,
        'page'          : page,
        'size'          : size
    }



def to_int(val, default):
    if val:
        try:
            val = int(val)
            if val:
                return val
            return default
        except:
            pass
    return default

class DotDict(dict):
    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, attr, value):
        self[attr] = value

    def __delattr__(self, attr):
        del self[attr]


def export_as_excel(data, file_name, excluded_cols=[]):

    df = pd.DataFrame(data)
    
    if excluded_cols and len(data):
        df = df.drop(excluded_cols, axis=1)


    buffer = BytesIO()
    
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{file_name}.xlsx"'
    
    return response