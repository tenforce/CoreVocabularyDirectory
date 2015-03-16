# SYSTEM
#
# VERSION				0.0.1

# Use the lastest version of ubuntu 
FROM ubuntu:latest
MAINTAINER pma
RUN apt-get update && apt-get upgrade -y
RUN apt-get install apache2 -y
RUN apt-get install virtuoso-opensource-6.1 -y
RUN apt-get install virtuoso-vad-conductor -y
RUN apt-get -y install rsyslog
ADD ./logentries.conf /etc/rsyslog.d/logentries.conf
COPY system/data/* /var/lib/virtuoso-opensource-6.1/db/data/
ADD data.ttl /var/lib/virtuoso-opensource-6.1/db/data/
ADD dcatods.ttl /var/lib/virtuoso-opensource-6.1/db/data/
COPY system /var/lib/virtuoso-opensource-6.1/vsp/vdm
RUN ls /var/lib/virtuoso-opensource-6.1/vsp/vdm
COPY virtuoso-setup/virtuoso.ini /etc/virtuoso-opensource-6.1/virtuoso.ini
EXPOSE 8890 
EXPOSE 1111
RUN cd /var/lib/virtuoso-opensource-6.1/db \
    && virtuoso-t +wait -c /etc/virtuoso-opensource-6.1/virtuoso.ini \
    && ( cat /var/lib/virtuoso-opensource-6.1/vsp/vdm/vhost_export.vspx.isql ; echo "ld_dir('/var/lib/virtuoso-opensource-6.1/db/data', '*.ttl', 'http://vocabs.tenforce.com/DAV');\nrdf_loader_run();\nexec('checkpoint');\nshutdown();registry_set ('__sparql_endpoint_debug', '1');" ) | isql-vt -U dba -P dba

CMD ["/usr/bin/virtuoso-t","+wait", "+foreground","-c","/etc/virtuoso-opensource-6.1/virtuoso.ini"]
