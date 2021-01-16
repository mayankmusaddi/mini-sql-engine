import sys
import sqlparse
from database import Database

DEFAULT_METADATA = "metadata.txt"

def evaluate(n1, n2, op):
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

def evaluate(name, column):
    options = {
        'MAX'  : max(column),
        'MIN'  : min(column),
        'SUM'  : sum(column),
        'COUNT': len(column),
        'AVG'  : sum(column)/len(column),
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
        table_names = str(self.tokens['tables']).split(',')

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

        return evaluate(n1,n2,op)

    def process_where(self):
        conditions = self.tokens['where']
        conditions = [condition for condition in conditions if str(condition)!=' ' and str(condition)!='WHERE']

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
        result = []
        for function in functions:

            if len(function.tokens) != 2 or len(function[1].tokens) != 3:
                print("INVALID AGGREGATE FUNCTION")
                exit(0)

            func_name = str(function[0]).upper()
            aggr_name = str(function[1][1])

            if aggr_name not in self.output_names:
                print("INVALID COLUMN NAME IN AGGREGATE FUNCTION")
                exit(0)
            
            aggr_ind = self.output_names.index(aggr_name)
            aggr_col = [row[aggr_ind] for row in table]

            aggr = evaluate(func_name, aggr_col)
            result.append(aggr)
        return result

    def process_group(self):
        group_name = str(self.tokens['group'])
        columns = self.tokens['columns']

        if group_name not in self.output_names:
            print("INVALID GROUP BY COLUMN NAME")
            exit(0)

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
            func_name = str(function[0]).upper()
            func_para = str(function[1])
            group_names.append( func_name+func_para)

        self.output = group_table
        self.output_names = group_names

    def run(self):
        self.join_tables()

        # process where
        if 'where' in self.tokens:
            self.process_where()

        # process group by
        if 'group' in self.tokens:
            self.process_group()

        # process aggregates
        
        # process order by
        # filter columns

        # process distinct



def run(statement, database):
    queries = sqlparse.format(statement, keyword_case = 'upper')
    queries = sqlparse.parse(queries)
    for query in queries:
        q = Query(query,database)
        q.parse_query()

def test(statement):
    database = Database(DEFAULT_METADATA)
    queries = sqlparse.format(statement, keyword_case = 'upper')
    queries = sqlparse.parse(queries)
    q = Query(queries[0],database)
    q.run()
    return q

if __name__ == "__main__":
    # statement = sys.argv[1]
    # run(statement   , database)
    database = Database(DEFAULT_METADATA)
    statement = "select max(A), sum(C) from table1,table2,table3 group by A"
    print(statement)
    queries = sqlparse.format(statement, keyword_case = 'upper')
    queries = sqlparse.parse(queries)
    q = Query(queries[0],database)
    q.run()

    print(q.output_names)
    print(q.output)
    print(len(q.output))