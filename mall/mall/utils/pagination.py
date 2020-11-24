from rest_framework.pagination import PageNumberPagination



class StandardResultsSetPagination(PageNumberPagination):
    '''自定义分页类'''

    page_size = 2  # 指定默认每一页显示多少条数据
    # page_size_query_param = 'page'  # 前端用来显示第几页的查询关键字,默认就是page
    page_size_query_param = 'page_size'
    max_page_size = 20  # 每页最大显示多少条数据