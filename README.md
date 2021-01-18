# mini-sql-engine

## Introduction

SQL or the Structured Query Language is an essential domain-specific language designed for managing data in a relational database management system. It serves as an Interface between the Functional API and the Database and so it becomes of utmost importance to understand how it may have been constructed. To provide an insight into this, an attempt of making a simple or a mini version of SQL using python has been showcased here.

A Mini SQL Engine which runs a subset of queries using Command Line Interface. 

### Dataset

#### Tables:
 - CSV files where the table name would be same as the csv file name inside the `files` folder
 - The data in the csv files contains only comma separated integers 

#### Metadata:
Metadata specifies all the table names and their respective column names loaded in the database.
For this a file named `metadata.txt` should be present in `files` folder having the following format.

\<begin_table\> <br />
\<table_name\>  <br />
\<attribute1\>  <br />
...           <br />
\<attributeN\>  <br />
\<end_table\>   <br />

Column names should be uniques across all tables and hence queries should not be preceded by table names.

### Queries

This Engine supports the following types of queries

- **Select queries:** Example - `Select * from table_name;`.
- **Project Columns:** Example - `Select col1, col2 from table_name;`.
- **Aggregate Function:** Sum, average, max, min and count are supported. Example - `Select max(col1) from table_name;`.
- **Distinct:** Example - `Select distinct col1, col2 from table_name;`.
- **Where:** Also supports queries with multiple tables. Example - `Select col1, col2 from table_name1, table_name2 where col1=val1 and col2=val2;`
- **Join:** Projection of one or more(including all the columns) from two tables with one join
condition. Example - `Select col1, col2 from table1,table2 where col1=col2;`.
- **Group By:** Grouping of columns based on aggregate functions. Example - `Select col1, COUNT(col2) from table_name group by col1;`.
- **Order By:** Ordering the rows based on the ascending/descending order of a particular column as queried. Example - `Select col1,col2 from table_name order by col1 ASC|DESC;`.

It also handles invalid queries and prints appropriate error statements.

## Running the code
`pip install -r requirements.txt`

`./run.sh <Query in double quotes>`

There are some sample queries in test.sh. You can run them by the command `./test.sh`