./run.sh "select * from table1 group by A;"

./run.sh "select A, max(B), A from table1 group by A;"

./run.sh "select A, max(B) from table1 group by B;"

./run.sh "select A, sum(B), avg(C), max(D), min(E), count(F)  from table1,table2,table3 group by A;"

./run.sh "select A, sum(B), avg(C), max(D), min(E), count(F)  from table1,table2,table3 group by A order by A desc;"

./run.sh "select distinct max(A), sum(B), D from table1,table2,table3 group by D order by D desc;"

./run.sh "select A,D from table1,table2,table3 order by F desc;"

./run.sh "select A, C, D  from table1,table2,table3 order by F desc;"

./run.sh "select * from table1 order by C;"

./run.sh "select * from table1 order by D;"

./run.sh "select * from table1,table2 order by D;"

./run.sh "select * from table1,table4 order by D;"

./run.sh "select F from table1,table2 order by D;"

./run.sh "select max(A), E from table1,table2,table3;"

./run.sh "select max(A),min(F),sum(B),avg(C),count(D) from table1,table2,table3;"

./run.sh "select max(A),min(F),sum(B),avg(C),count(D) from table1,table2,table3 order by F;"