class Query:
    """
    Query class to represent an AWS OpenSearch query domain-specific language (DSL),
    providing a range of search options. Query objects will be used by the Client
    search method and used in OpenSearch searches.

    ...

    Attributes
    ----------
    query: dict
        dictionary containing the query field (dict key) and the query text 
        (dict value).
    size: int, optional
        number of results to return. default is 10.
    

    Methods
    -------
    query_dsl: str
        returns the query in the OpenSearch Query DSL format
    size: int
        returns the number of results the query is allowed to return in the search.
    """

    def __init__(self, query_params, size=10):
        self.query_params = query_params
        self.query_dsl_formatted = self.__build_query_dsl(query_params)
        self.query_size = size 

    def query_dsl(self):
        """Returns the query parameters in the AWS OpenSearch Query DSL format"""
        return self.query_dsl_formatted

    def size(self):
        """Returns the number of results the query is allowed to return in the search"""
        return self.query_size

    def __build_query_dsl(self, query_params):
        query_structure = '{{"query": {{ "bool": {{"must": [{}] }} }} }}'
        query_param_structure = '{{ "match": {{ "{}": "{}" }} }}, '
        query_param_formatted = ''

        query_param_formatted, query_params = self.__build_range(query_params)

        for param in query_params:
            query_param_formatted = query_param_formatted + query_param_structure.format(param, query_params[param])
        
        query_dsl = query_structure.format(query_param_formatted)

        return query_dsl

    def __build_range(self, query_params):
        query_range_structure = '{{ "match": {{ "date": {{ {}{} }} }} }}, '
        query_range_formatted = ""
        try:
            start_date = '"gte": "{}"'.format(query_params.pop("start_date"))
        except:
            start_date = ""
        try:
            end_date = '"lte": "{}"'.format(query_params.pop("end_date"))
            if start_date != "":
                end_date = ", " + end_date
        except:
            end_date = ""

        if start_date != "" or end_date != "":
            query_range_formatted = query_range_structure.format(start_date, end_date)
        
        return query_range_formatted, query_params
        

        

    def __repr__(self):
        return self.query_dsl_formatted