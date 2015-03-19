#!/bin/bash

function name_link {
		echo \"name\": \"$1\" ",";
    l=`echo $1 | sed 's/_/%20/g'`;
		echo \"link\": \"http://vocabs.tenforce.com/vdm/search?id=$l\",
}

function end_comma {
 		if [ $1 != $2 ] 
		then
				echo -n "," ;
		fi;
}

# set -x 
( echo "{";
	echo \"name\": \"Core Vocabulary Mappings\" ",";
	echo \"children\": "[" ;

	fl=`cat all.links | awk -F"|" '{print $2;}' | sort -u`
	lfl=`echo $fl | awk '{print $NF}'`
	for f in $fl
	  do
		  echo "{" 
			name_link $f;
			echo \"children\": "["
			 
			  cl=`cat all.links | egrep $f"\|" | awk -F"|" '{print $4;}' | sort -u`
				lcl=`echo $cl | awk '{print $NF}'`
				for c in $cl
				do	
					  echo "{" 
						name_link $c;
						echo \"children\": "["

						pl=`cat all.links | egrep $f"\|" | egrep "\|"$c"\|" | awk -F"|" '{print $5;}' | sort -u`
						lpl=`echo $pl | awk '{print $NF}'`
						for p in $pl
						do	
						  echo "{";
							name_link $p;
							echo \"children\": "["

							el=`cat all.links | egrep $f"\|" | egrep "\|"$c"\|" | egrep "\|"$p"\|" | awk -F"|" '{print $7;}' | sort -u`
							lel=`echo $el| awk '{print $NF}'`
							for e in $el
							do	
							  echo -n "{"
								name_link $e;
								echo \"children\": "["
								# Children

								el5=`cat all.links | egrep $f"\|" | egrep "\|"$c"\|" | egrep "\|"$p"\|" |  egrep "\|"$e"\|" | awk -F"|" '{print $9;}' | sort -u`
								lel5=`echo $el5| awk '{print $NF}'`
								for e5 in $el5
								do	
										echo -n "{"
										name_link $e5
										echo -n \"size\": 200;
										# End
                    echo -n "}"
										end_comma $e5 $lel5
       					done
								# End
								
                echo -n " ] }"
								end_comma $e $lel
       				done
  					  echo "] }";
							end_comma $p $lpl
    				done
 		    	  echo "] }";
						end_comma $c $lcl
 				done
			  echo " ] }";
				end_comma $f $lfl
		done
	echo "] }";
)
