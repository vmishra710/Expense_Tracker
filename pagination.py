from typing import List, Any

def paginate_query_result(data : List[Any],
                          total_count : int,
                          limit : int,
                          offset : int):
    has_more = offset + limit < total_count
    return{
        'total_count' : total_count,
        'limit' : limit,
        'offset' : offset,
        'has_more' : has_more,
        'expenses' : data
    }