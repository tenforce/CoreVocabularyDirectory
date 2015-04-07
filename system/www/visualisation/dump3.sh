#!/bin/bash

function name_link {
		link=`echo $* | awk -F@ '{print $1;}' | tr -d \"`
		name=`echo $* | awk -F@ '{print $2;}' | tr -d \" | sed 's?http://www.w3.org/2004/02/skos/core#??g'`
		echo \"link\": \"$link\",
		echo \"name\": \"$name\",;
}

function end_comma {
		n1=`echo $1 | tr -d '[[:space:]]'`;
    n2=`echo $2 | tr -d '[[:space:]]'`;
 		if [ "$n1" != "$n2" ] 
		then
				echo -n "," ;
		fi;
}

( cat $1 | tr "\t" "\|" > all1.links ;
  cat all1.links | awk -F\| 'BEGIN{OFS="|";}{print $1"@"$2,$3"@"$4,$5"@"$6,$7"@"$8,$9"@"$10,$11"@"$12;}' > all2.links;
	cat all2.links | awk -F"|" '{print $1;}' | sort -u > c1.txt
	lfl=`tail -1 c1.txt`
	cat c1.txt | while read c1;
	  do
		  echo "{" 
			name_link \"$c1\";
			echo \"size\": \"100\",
			echo \"children\": "["
			 
			  cat all2.links | grep "$c1" | awk -F"|" '{print $2;}' | sort -u > c2.txt
				lcl=`tail -1 c2.txt`
				cat c2.txt | while read c2;
				do	
					  echo "{" 
						name_link \"$c2\";
						echo \"size\": \"100\",
						echo \"children\": "["

						cat all2.links | grep "$c1" | grep "$c2" | awk -F"|" '{print $3;}' | sort -u > c3.txt
						lpl=`tail -1 c3.txt`
						cat c3.txt | while read c3;
						do	
						  echo "{";
							name_link \"$c3\";
							echo \"children\": "["
							cat all2.links | grep "$c1" | grep "$c2" | grep "$c3" | awk -F"|" '{print $4;}' | sort -u > c4.txt
						  lel=`tail -1 c4.txt`
							cat c4.txt | while read c4;
							do	
							  echo -n "{"
								name_link \"$c4\";
								echo \"children\": "["
								# Children

								cat all2.links | grep "$c1" | grep "$c2" | grep "$c3" | grep "$c4" | awk -F"|" '{print $5;}' | sort -u > c5.txt
								lel5=`tail -1 c5.txt `
								cat c5.txt | while read c5;
								do	
										echo -n "{"
										name_link \"$c5\"
										echo \"children\": "["
										
										cat all2.links | grep "$c1" | grep "$c2" | grep "$c3" | grep "$c4" | grep "$c5" | awk -F"|" '{print $6;}' | sort -u > c6.txt
										lel6=`tail -1 c6.txt`
										cat c6.txt | while read c6;
										do	
												echo -n "{"
												name_link \"$c6\"
												echo -n \"size\": 150
												# more here...
												echo -n "}"
												end_comma "$c6" "$lel6"
       							done
										# End
                    echo -n "] }"
										end_comma "$c5" "$lel5"
       					done
                echo -n " ] }"
								end_comma "$c4" "$lel"
       				done
  					  echo "] }";
							end_comma "$c3" "$lpl"
    				done
 		    	  echo "] }";
						end_comma "$c2" "$lcl"
 				done
			  echo " ] }";
				end_comma "$c1" "$lfl"
		done
)
rm -rf c?.txt all?.links

