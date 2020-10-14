import logging

class QueryExecutor(object):
    def __init__(self, config):
        self.config = config
        self.log = logging.getLogger()

    def execute_query(self, select_cols, doc_type, filters=None, get_single_result=True,
                      orderby=None):
        """
        :param select_cols: comma separated columns list (eg select_cols="col1,col2,col3")
        :param doc_type: document type
        :param filters: (dict) {key1: val1, key2: val2}
        :param get_single_result: (bool)
        :return: executed query result
        """
        query = f"select {select_cols} from `{self.config.CB_INSTANCE}` where type='{doc_type}'"
        if filters:
            for key, val in filters.items():
                if isinstance(val, list):
                    query = f"{query} and {key} in {val} "

                else:
                    query = f"{query} and {key} = '{val}' "
        if orderby:
            query = query + str(orderby)
        if '>' in query:
            query = query.replace("> =", ">=")
        res = self.config.cb.n1ql_query(query)
        self.log.debug("query executed : {}".format(query))
        if get_single_result:
            res = res.get_single_result()
        return res

    def execute_update_query(self, update_cols, value, doc_type, filters=None):
        query = f'update `{self.config.CB_INSTANCE}` set {update_cols} = "{value}" where type = {doc_type}'
        if filters:
            for key, val in filters.items():
                query = f'{query} and {key}="{val}"'
        res = self.config.cb.n1ql_query(query)
        return True if res else False

    def execute_delete_query(self, id, doc_type):
        del_query = f'delete from `{self.config.CB_INSTANCE}` where type = {doc_type} and meta().id = "{id}"'
        res = self.config.cb.n1ql_query(del_query)
        return True if res else False
