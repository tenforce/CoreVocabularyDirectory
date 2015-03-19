DOCKER=docker

SYSTEM=system

data: data2.ttl dcatods.ttl data.ttl
	( cd system; ./configure.sh )

data2.ttl: excelfiles/Core_Vocabularies_v1.1_v0.31.xlsx system/scripts/cvxsl2mdr.py 
	system/scripts/cvxsl2mdr.py excelfiles/Core_Vocabularies_v1.1_v0.31.xlsx > data2.ttl

data.ttl: excelfiles/Core_Vocabularies_v1.3.xlsx system/scripts/cvxsl2vdm.py 
	system/scripts/cvxsl2vdm.py excelfiles/Core_Vocabularies_v1.3.xlsx > data.ttl

dcatods.ttl: excelfiles/DCatVocabularies-v0.1.xlsx system/scripts/dcatxsl2mdr.py 
	system/scripts/dcatxsl2mdr.py excelfiles/DCatVocabularies-v0.1.xlsx > dcatods.ttl

vdm.tgz: data
	mkdir vdm
	cp -r system/* vdm
	cp excelfiles/*.xlsx vdm/www
	cp *.ttl vdm
	cp system/data/vdm.ttl vdm
	tar cvzf vdm.tgz vdm
	rm -rf vdm

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
	sudo ${DOCKER} rm -f `sudo ${DOCKER} ps -a -q`
	sudo ${DOCKER} rmi `sudo ${DOCKER} images -q`
	sudo service ${DOCKER} restart
