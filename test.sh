./run.sh "select distinct max(A), sum(B), D from table1,table2,table3 group by D order by D desc"
./run.sh "select A,D from table1,table2,table3 order by F desc"