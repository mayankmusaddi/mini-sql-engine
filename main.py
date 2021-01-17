import sys
import sqlparse
from database import Database

DEFAULT_METADATA = "metadata.txt"

def evaluate_exp(n1, n2, op):
    options = {
        '='  : n1 == n2,
        '>=' : n1 >= n2,
        '<=' : n1 <= n2,
        '>'  : n1 > n2,
        '<'  : n1 < n2,
    }

    # Error handling
    if op not in options:
        print("INVALID COMPARISON OPERATOR")
        exit(0)

    return options[op]

def evaluate_aggr(name, column):
    options = {
        'max'  : max(column),
        'min'  : min(column),
        'sum'  : sum(column),
        'count': len(column),
        'avg'  : sum(column)/len(column),
    }

    # Error handling
    if name not in options:
        print("INVALID AGGREGATE FUNCTION NAME")
        exit(0)

    return options[name]

class Query:
    def __init__(self, query, database):
        self.query = query
        self.database = database
        self.distinct = False
        self.tokens = {}
        self.output = []
        self.output_names = []

        self.parse_query()
    
    def get_table(self, column):
        for table in self.database.schema:
            columns = self.database.schema[table]
            if column in columns:
                return table

    def parse_query(self):
        tokens = self.query.tokens
        tokens = [token for token in tokens if str(token)!=' ' and str(token)!=';']
        token_len = len(tokens)

        if(token_len < 4):
            print("INVALID SYNTAX")
            exit(0)
        
        ptr = 0
        # SELECT
        if ptr < token_len and str(tokens[ptr]) != "SELECT":
            print("QUERY SHOULD START WITH SELECT")
            exit(0)
        ptr+=1

        # DISTINCT
        if ptr < token_len and str(tokens[ptr]) == "DISTINCT":
            self.distinct = True
            ptr+=1
        
        # COLUMNS
        if ptr < token_len:
            self.tokens['columns'] = tokens[ptr]
            ptr+=1

        # FROM
        if ptr < token_len and str(tokens[ptr]) != "FROM":
            print("QUERY SHOULD CONTAIN FROM")
            exit(0)
        ptr+=1

        # TABLES
        if ptr < token_len:
            self.tokens['tables'] = tokens[ptr]
            ptr+=1

        # WHERE
        if ptr < token_len and len(str(tokens[ptr])) > 5 and str(tokens[ptr])[:5] == "WHERE":
            self.tokens['where'] = tokens[ptr]
            ptr+=1

        # GROUP BY
        if ptr < token_len and str(tokens[ptr]) == "GROUP BY":
            ptr+=1
            if ptr >= token_len:
                print("GROUP BY HAS NO ARGUMENTS")
                exit(0)
            self.tokens['group'] = tokens[ptr]
            ptr+=1

        # ORDER BY
        if ptr < token_len and str(tokens[ptr]) == "ORDER BY":
            ptr+=1
            if ptr >= token_len:
                print("ORDER BY HAS NO ARGUMENTS")
                exit(0)
            self.tokens['order'] = tokens[ptr]
            ptr+=1

        if ptr < token_len:
            print("INVALID SYNTAX")
            exit(0)

    def join_tables(self):
        # table_names = str(self.tokens['tables']).split(',')
        table_tokens = self.tokens['tables']

        if type(table_tokens) != sqlparse.sql.IdentifierList and type(table_tokens) != sqlparse.sql.Identifier:
            print("INVALID SELECTION CRITERIA")
            exit(0)
        
        table_tokens = table_tokens.tokens
        table_tokens = [table_token for table_token in table_tokens if str(table_token) != ' ' and str(table_token) != ',']
        table_names = [str(token) for token in table_tokens]

        # Error Handling
        if len(table_names) != len(set(table_names)):
            print("TABLE NAMES DUPLICATED")
            exit(0)
        
        for table_name in table_names:
            if table_name not in self.database.schema:
                print("TABLE NOT PRESENT IN DATABASE")
                exit(0)

        joined_table = [[]]
        col_names = []
        for table_name in table_names:
            col_names += self.database.schema[table_name]
            temp = []
            for row1 in joined_table:
                for row2 in self.database.table_data[table_name]:
                    temp.append(row1+row2)
            joined_table = temp
        
        self.output = joined_table
        self.output_names = col_names

    def satisfies(self, row, condition):

        if type(condition) != sqlparse.sql.Comparison:
            print("INVALID CONDITION TYPE")
            exit(0)

        condition = condition.tokens
        condition = [c for c in condition if str(c)!=' ']

        # Error Handling
        if len(condition) != 3:
            print("INVALID CONDITON SPECIFIED")
            exit(0)

        c1 = str(condition[0])
        c2 = str(condition[2])
        op = str(condition[1])

        if c1.isnumeric():
            n1 = int(c1)
        else:
            if c1 not in self.output_names:
                print("INVALID COLUMN IN WHERE CONDITION")
                exit(0)
            n1 = row[self.output_names.index(c1)]

        if c2.isnumeric():
            n2 = int(c2)
        else:
            if c2 not in self.output_names:
                print("INVALID COLUMN IN WHERE CONDITION")
                exit(0)
            n2 = row[self.output_names.index(c2)]

        return evaluate_exp(n1,n2,op)

    def process_where(self):

        if len(self.output) == 0 or len(self.output[0]) == 0:
            return

        conditions = self.tokens['where']
        conditions = [condition for condition in conditions if str(condition)!=' ' and str(condition)!='WHERE' and str(condition)!=';']

        # Error Handling
        if len(conditions) != 1 and len(conditions) != 3:
            print("INVALID NUMBER OF WHERE CONDITIONS SPECIFIED")
            exit(0)

        where_table = []
        for row in self.output:
            c1 = self.satisfies(row, conditions[0])
            c = c1
            if len(conditions) == 3:
                c2 = self.satisfies(row, conditions[2])
                if str(conditions[1]) == 'AND':
                    c = c1 and c2
                elif str(conditions[1]) == 'OR':
                    c = c1 or c2
            if c:
                where_table.append(row)
        self.output = where_table

    def aggregate(self, table, functions):

        if len(table) == 0 or len(table[0]) == 0:
            return []

        result = []
        for function in functions:

            if len(function.tokens) != 2 or len(function[1].tokens) != 3:
                print("INVALID AGGREGATE FUNCTION")
                exit(0)

            func_name = str(function[0]).lower()
            aggr_name = str(function[1][1])

            if aggr_name not in self.output_names:
                print("INVALID COLUMN NAME IN AGGREGATE FUNCTION")
                exit(0)
            
            aggr_ind = self.output_names.index(aggr_name)
            aggr_col = [row[aggr_ind] for row in table]

            aggr = evaluate_aggr(func_name, aggr_col)
            result.append(aggr)
        return result

    def process_group(self):

        group_name = str(self.tokens['group'])
        columns = self.tokens['columns']

        if group_name not in self.output_names:
            print("INVALID GROUP BY COLUMN NAME")
            exit(0)

        if type(columns) != sqlparse.sql.IdentifierList and type(columns) != sqlparse.sql.Identifier and type(columns) != sqlparse.sql.Function:
            print("INVALID SELECTION CRITERIA FOR GROUP BY")
            exit(0)

        if type(columns) == sqlparse.sql.Function:
            columns = [columns]
        else:
            columns = columns.tokens

        columns = [x for x in columns if str(x)!=' ' and str(x)!=',']
        functions = []
        for column in columns:
            if type(column) != sqlparse.sql.Function:
                if str(column) != group_name:
                    print("INVALID GROUP BY COLUMN LIST")
                    exit(0)
            else:
                functions.append(column)

        group_ind = self.output_names.index(group_name)
        group_column = list(set([row[group_ind] for row in self.output]))

        group_table = []
        for num in group_column:
            subtable = [row for row in self.output if row[group_ind] == num]
            result = self.aggregate(subtable, functions)
            group_table.append([num] + result)

        group_names = [group_name]
        for function in functions:
            func_name = str(function[0]).lower()
            func_para = str(function[1])
            group_names.append( func_name+func_para)

        self.output = group_table
        self.output_names = group_names

    def process_aggregates(self):

        columns = self.tokens['columns']

        if str(columns) == '*':
            return
        if type(columns) != sqlparse.sql.IdentifierList and type(columns) != sqlparse.sql.Identifier and type(columns) != sqlparse.sql.Function:
            print("INVALID SELECTION CRITERIA")
            exit(0)

        if type(columns) == sqlparse.sql.Function:
            columns = [columns]
        else:
            columns = columns.tokens

        columns = [x for x in columns if str(x)!=' ' and str(x)!=',']

        functions = []
        for column in columns:
            if type(column) == sqlparse.sql.Function:
                functions.append(column)
        
        if len(functions) == 0:
            return
        if len(functions) != len(columns):
            print("CANNOT SELECT AGGREGATE AND COLUMN TOGETHER")
            exit(0)

        aggr_table = [self.aggregate(self.output, functions)]
        aggr_names = []
        for function in functions:
            func_name = str(function[0]).lower()
            func_para = str(function[1])
            aggr_names.append( func_name+func_para)

        self.output = aggr_table
        self.output_names = aggr_names

    def process_order(self):

        if len(self.output) == 0 or len(self.output[0]) == 0:
            return

        order = self.tokens['order']
        if type(order) != sqlparse.sql.Identifier:
            print("INVALID ORDER BY ARGUMENTS")
            exit(0)
        order = order.tokens
        order = [x for x in order if str(x)!=' ' and str(x)!=',']
        
        # Error Handling
        if len(order) > 2 or len(order) == 0:
            print("INVALID ORDER BY ARGUMENTS")
            exit(0)

        order_name = str(order[0])
        order_type = 'ASC'
        if len(order) == 2:
            order_type = str(order[1])

        if order_name not in self.output_names or (order_type != 'ASC' and order_type != 'DESC'):
            print("INVLAID ORDER BY ARGUMENTS")
            exit(0)

        sort_order = False if order_type == 'ASC' else True
        order_index = self.output_names.index(order_name)
        self.output.sort(key = lambda x:x[order_index], reverse = sort_order)

    def filter_columns(self):

        columns = self.tokens['columns']

        if str(columns) == '*':
            return
        if type(columns) != sqlparse.sql.IdentifierList and type(columns) != sqlparse.sql.Identifier and type(columns) != sqlparse.sql.Function:
            print("INVALID SELECTION CRITERIA")
            exit(0)

        if type(columns) == sqlparse.sql.Function:
            columns = [columns]
        else:
            columns = columns.tokens

        columns = [x for x in columns if str(x)!=' ' and str(x)!=',']

        filtered_table = []
        filtered_names = []
        for column in columns:
            if type(column) == sqlparse.sql.Function:
                col = (str(column[0]).lower() + str(column[1]))
            else:
                col = str(column)
            
            if col not in self.output_names:
                print("INVALID SELECT COLUMN ENTRY")
                exit(0)

            filtered_names.append(col)
            col_index = self.output_names.index(col)

            if len(self.output) != 0 and len(self.output[0]) != 0:
                filtered_table.append([row[col_index] for row in self.output])
        
        self.output = list(map(list, zip(*filtered_table)))
        self.output_names = filtered_names
  
    def process_distinct(self):
        distinct_table = []
        is_unique = {}
        for row in self.output:
            if tuple(row) not in is_unique:
                is_unique[tuple(row)] = True
                distinct_table.append(row)
        self.output = distinct_table
        # return
    
    def print_output(self):
        output_names = []
        for name in self.output_names:
            if '(' in name:
                col = name[name.index('(')+1:-1]
                table = self.get_table(col)
                output_name = name[:name.index('(')+1] + table+'.'+col + ')'
            else:
                table = self.get_table(name)
                output_name = table+'.'+name
            output_names.append(output_name)
        print(','.join(output_names))
        for row in self.output:
            print(','.join(map(str, row)))

    def run(self):
        # process from
        self.join_tables()

        # process where
        if 'where' in self.tokens:
            self.process_where()

        # process group by
        if 'group' in self.tokens:
            self.process_group()

        # process aggregates
        if 'group' not in self.tokens:
            self.process_aggregates()

        # process order by
        if 'order' in self.tokens:
            self.process_order()

        # filter columns
        self.filter_columns()

        # process distinct
        if self.distinct:
            self.process_distinct()

def run(statement, database):
    queries = sqlparse.format(statement, keyword_case = 'upper')
    queries = sqlparse.parse(queries)
    for query in queries:
        if str(query)[-1] != ';':
            print("QUERIES SHOULD END WITH SEMICOLON")
            exit(0)
        q = Query(query,database)
        q.run()
        q.print_output()

def test(statement):
    database = Database(DEFAULT_METADATA)
    queries = sqlparse.format(statement, keyword_case = 'upper')
    queries = sqlparse.parse(queries)
    q = Query(queries[0],database)
    # q.run()   
    return q

if __name__ == "__main__":
    statement = sys.argv[1]
    database = Database(DEFAULT_METADATA)
    run(statement, database)