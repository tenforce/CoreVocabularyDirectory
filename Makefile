DOCKER=docker

SYSTEM=system

data: ttldata visualisations
	( cd system; ./configure.sh )

# The following will create the .ttl data files from the respective
# excel files. The excel files are required to have a fixed format and
# changes in labels are not allowed (program will about if the sheets
# are not available or labels are not what are expected).

ttldata: data2.ttl dcatods.ttl data.ttl 

data2.ttl: excelfiles/Core_Vocabularies_v1.1_v0.31.xlsx system/scripts/cvxsl2mdr.py 
	system/scripts/cvxsl2mdr.py excelfiles/Core_Vocabularies_v1.1_v0.31.xlsx > data2.ttl

data.ttl: excelfiles/Core_Vocabularies_v1.3.xlsx system/scripts/cvxsl2vdm.py 
	system/scripts/cvxsl2vdm.py excelfiles/Core_Vocabularies_v1.3.xlsx > data.ttl

dcatods2.ttl: excelfiles/DCatVocabularies-v0.1.xlsx system/scripts/dcatxsl2mdr.py 
	system/scripts/dcatxsl2mdr.py excelfiles/DCatVocabularies-v0.1.xlsx > dcatods2.ttl

dcatods.ttl: excelfiles/DCatVocabularies-v0.2.xlsx system/scripts/cvxsl2vdm.py 
	system/scripts/cvxsl2vdm.py excelfiles/DCatVocabularies-v0.2.xlsx > dcatods.ttl

# This will create the necessary .json files representing the results
# of the two queries found in system/www/visualisation/dataquery.org
# The two queries are not automatically run, since the system needs to 
# be installed and the data accessible for the queries to be correct.

visualisations: system/www/visualisation/cvflare.json system/www/visualisation/dcatflare.json 

system/www/visualisation/cvflare.json: system/www/visualisation/all.links system/www/visualisation/dump3.sh
	( cd system/www/visualisation; ./dump3.sh all.links > cvflare.json )

system/www/visualisation/dcatflare.json: system/www/visualisation/all-dcat.links system/www/visualisation/dump3.sh
	( cd system/www/visualisation; ./dump3.sh all-dcat.links > dcatflare.json )

# Gather together all the data which is intended to be made public
# (refered to on the main page).

www/public_data:
	mkdir -p system/www/public_data
	cp excelfiles/Core_Vocabularies_v1.3.xlsx system/www/public_data
	cp excelfiles/DCatVocabularies-v0.2.xlsx system/www/public_data
	cp excelfiles/EuroVocmappings_v0.03-1.xlsx system/www/public_data
	cp excelfiles/Core_Vocabularies_Mapping_Template.xlsx system/www/public_data
	cp system/data/vdm.ttl system/www/public_data
	cp system/data/skos.rdf system/www/public_data
	cp system/data/adms*.rdf system/www/public_data
	cp system/data/dcterms.rdf system/www/public_data

# This will create a 'tar' file with all the system components in it.
# This can then be transfered to the remote system for installation.

vdm.tgz: data www/public_data
	mkdir -p vdm
	cp -r system/* vdm
	mkdir -p vdm/public_data
	cp excelfiles/*.xlsx vdm/www/public_data
	cp system/data/vdm.ttl vdm/www/public_data
	cp system/data/skos.rdf vdm/www/public_data
	cp system/data/adms*.rdf vdm/www/public_data
	cp *.ttl vdm
	cp system/data/vdm.ttl vdm
	tar cvzf vdm.tgz vdm
	rm -rf vdm

# The following commands are to use the docker image while developing
# the system. The main targets are: 
#     image - to build the docker image
#     run   - to start the docker image and allow the pages to the accessed

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
