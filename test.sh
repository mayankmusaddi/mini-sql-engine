./run.sh "select * from table1;"

./run.sh "select * from table1, table2;"

./run.sh "select A, B from table1, table2;"

./run.sh "select B, D2 from table1, table2;"

./run.sh "select distinct B from table1;"

./run.sh "select A, B2 from table1, table2 where A > 900 AND D2 < 200;"

./run.sh "select * from table1, table2 where B > D2;"

./run.sh "select A, B, D2 from table1, table2 where B = D2;"

./run.sh "select A, B, C from table1, table2;"

./run.sh "select distinct A, D2 from table1, table2;"

./run.sh "select distinct A, B2 from table1, table2;"

./run.sh "Select max(A) from table1, table2 where A = D2;"

./run.sh "select A, B2 from table1, table2 where A > 900 AND B2 < 100;"

./run.sh "select A, B2 from table1, table2 where A > 900 AND B2 = 311;"

./run.sh "Select B,B2 from table1,table2 where B=B2;"

./run.sh "Select B, B2 from table1, table2 where A > 0 and B = B2;"

./run.sh "Slect B, B2 from table1, table2 where A > 0 and B = B2;"

./run.sh "Select B, B2 table1, table2 where A > 0 and B = B2;"

./run.sh "Select"

./run.sh "Select B, B2 from table1, table2 where A > 0 and B = B2"

./run.sh "Select B, B2 from table1, table2 where A > 0 xor B = B2;"

./run.sh "Select B, B2 from table1, table2 where A > 0 and B = B2;"

./run.sh "Select B, B2 from table1, table2 wherre A > 0 and B = B2;"

./run.sh "B, B2 from table1, table2 where A > 0 and B = B2;"

./run.sh "from table1, table2 where A & 0 and B = B2;"


# ./run.sh "select distinct max(A), sum(B), D from table1,table2,table3 group by D order by D desc"
# ./run.sh "select A,D from table1,table2,table3 order by F desc"