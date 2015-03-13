DOCKER=docker

SYSTEM=system

data: data.ttl dcatods.ttl
	( cd system; ./configure.sh )

data.ttl: excelfiles/Core_Vocabularies_v1.1_v0.31.xlsx
	system/scripts/cvxsl2mdr.py excelfiles/Core_Vocabularies_v1.1_v0.31.xlsx > data.ttl

dcatods.ttl: excelfiles/DCatVocabularies-v0.1.xlsx
	system/scripts/dcatxsl2mdr.py excelfiles/DCatVocabularies-v0.1.xlsx > dcatods.ttl

image:	data
	sudo ${DOCKER} build -t mdrtest2 .
	sudo service ${DOCKER} restart

setup:
	sudo service apache2 stop
	sudo service virtuoso-opensource-6.1 stop

run: setup
	sudo ${DOCKER} run -p 80:80 -p 1111:1111 mdrtest2

clean:
	sudo ${DOCKER} rm mdrtest2
	sudo ${DOCKER} rmi mdrtest2
	sudo service ${DOCKER} restart

cleanall:
	sudo ${DOCKER} rm `sudo ${DOCKER} ps -a -q`
	sudo ${DOCKER} rmi `sudo ${DOCKER} images -q`
	sudo service ${DOCKER} restart
