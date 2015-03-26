DOCKER=docker

SYSTEM=system

data: data2.ttl dcatods.ttl data.ttl system/www/visualisation/cvflare.json system/www/visualisation/dcatflare.json 
	( cd system; ./configure.sh )

data2.ttl: excelfiles/Core_Vocabularies_v1.1_v0.31.xlsx system/scripts/cvxsl2mdr.py 
	system/scripts/cvxsl2mdr.py excelfiles/Core_Vocabularies_v1.1_v0.31.xlsx > data2.ttl

data.ttl: excelfiles/Core_Vocabularies_v1.3.xlsx system/scripts/cvxsl2vdm.py 
	system/scripts/cvxsl2vdm.py excelfiles/Core_Vocabularies_v1.3.xlsx > data.ttl

dcatods2.ttl: excelfiles/DCatVocabularies-v0.1.xlsx system/scripts/dcatxsl2mdr.py 
	system/scripts/dcatxsl2mdr.py excelfiles/DCatVocabularies-v0.1.xlsx > dcatods2.ttl

dcatods.ttl: excelfiles/DCatVocabularies-v0.2.xlsx system/scripts/cvxsl2vdm.py 
	system/scripts/cvxsl2vdm.py excelfiles/DCatVocabularies-v0.2.xlsx > dcatods.ttl

system/www/visualisation/cvflare.json: system/www/visualisation/all.links system/www/visualisation/dump3.sh
	( cd system/www/visualisation; ./dump3.sh all.links > cvflare.json )

system/www/visualisation/dcatflare.json: system/www/visualisation/all-dcat.links system/www/visualisation/dump3.sh
	( cd system/www/visualisation; ./dump3.sh all-dcat.links > dcatflare.json )

www/public_data:
	mkdir -p system/www/public_data
	cp excelfiles/Core_Vocabularies_v1.3.xlsx system/www/public_data
	cp excelfiles/DCatVocabularies-v0.2.xlsx system/www/public_data
	cp excelfiles/EuroVocmappings_v0.03-1.xlsx system/www/public_data
	cp excelfiles/Core_Vocabularies_Mapping_Template.xlsx system/www/public_data
	cp system/data/vdm.ttl system/www/public_data
	cp system/data/skos.rdf system/www/public_data
	cp system/data/dcterms.rdf system/www/public_data

vdm.tgz: data 
	mkdir -p vdm
	cp -r system/* vdm
	mkdir -p vdm/public_data
	cp excelfiles/*.xlsx vdm/www/public_data
	cp system/data/vdm.ttl vdm/www/public_data
	cp system/data/skos.rdf vdm/www/public_data
	cp *.ttl vdm
	cp system/data/vdm.ttl vdm
	tar cvzf vdm.tgz vdm
	rm -rf vdm

image:	data www/public_data
	sudo ${DOCKER} build -t mdrtest2 .
	sudo service ${DOCKER} restart

setup:
	sudo service apache2 stop
	sudo service virtuoso-opensource-6.1 stop

run: setup
	sudo ${DOCKER} run -p 80:80 -p 1111:1111 mdrtest2

clean:
	-rm -rf system/www/public_data vdm.tgz
	- sudo ${DOCKER} rm -f mdrtest2
	- sudo ${DOCKER} rmi mdrtest2
	- sudo service ${DOCKER} restart

cleanall:
	sudo ${DOCKER} rm -f `sudo ${DOCKER} ps -a -q`
	sudo ${DOCKER} rmi `sudo ${DOCKER} images -q`
	sudo service ${DOCKER} restart
