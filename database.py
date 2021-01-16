import csv

DATA_FOLDER = "files/"

class Database:
    def __init__(self, metadata):
        self.metadata_path = DATA_FOLDER+metadata
        self.schema = {}
        self.table_data = {}
        self.populate()
    
    def load_schema(self):
        try:
            with open(self.metadata_path, 'r') as metadata:
                table_start = False
                table_name = ''
                for line in metadata:

                    # to remove breakline at the end of each line
                    if line[-1] == '\n':
                        line = line[:-1]

                    if line == '<begin_table>':
                        table_start = True
                    elif line == '<end_table>':
                        self.schema[table_name] = column_names
                    elif table_start == True:
                        table_name = line
                        column_names = []
                        table_start = False
                    else:
                        column_names.append(line)
        except Exception as err:
            print(err)
            exit(0)

    def load_table(self):
        for table in self.schema:
            table_path = DATA_FOLDER+table+".csv"
            try:
                with open(table_path, 'r') as data:
                    data = csv.reader(data)
                    rows = []
                    for row in data:
                        rows.append([int(x) for x in row])
                    self.table_data[table] = rows
            except Exception as err:
                print(err)
                exit(0)
    
    def populate(self):
        self.load_schema()
        self.load_table()

if __name__ == "__main__":
    a = Database("metadata.txt")
    print(a.schema)
    print(a.table_data)