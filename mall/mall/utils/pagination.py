from rest_framework.pagination import PageNumberPagination



class StandardResultsSetPagination(PageNumberPagination):
    '''分页'''

    page_size = 2  # 默认每一页返回的数据
    page_size_query_param = 'page_size'
    max_page_size = 20