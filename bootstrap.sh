#!/usr/bin/env bash
#################################################################
echo "************* Bootstrapping started **********************"

# Kernel 3.2 not supported by docker (so used the 3.16 from backports)
echo "deb http://http.debian.net/debian wheezy-backports main" >> /etc/apt/sources.list.d/backports.list
apt-get update -y
apt-get install -y dkms virtualbox-guest-dkms virtualbox-guest-x11
apt-get install -y -t wheezy-backports linux-image-amd64 linux-headers-amd64 --force-yes
apt-mark hold linux-image-amd64

apt-get install -y ntp xinit xterm iceweasel gnome gnome-terminal gnome-shell
apt-get install -y gdm3 python-software-properties software-properties-common
apt-get install -y python python3 emacs xsltproc make autoconf redland-utils
apt-get install -y rasqal-utils gawk dos2unix emacs curl
apt-get purge -y *docker* 
dpkg-reconfigure gdm3
# Python 3 tools and some libraries which will be needed
apt-get install -y python3-setuptools python-setuptools
easy_install3 rdflib
easy_install3 xlrd
easy_install SPARQLWrapper

#################################################################
# Docker setup (docker is a different thing on wheezy), so take
# from main site.
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 36A1D7869245C8950F966E92D8576A8BA88D21E9
curl -ksSL https://get.docker.com/ | sh
groupadd docker
gpasswd -a vagrant docker
usermod -aG docker vagrant

#################################################################
# Set the default values for the debconf questions
#
apt-get install -y debconf-utils
echo "virtuoso-opensource-7.1 virtuoos-opensource-7.1/dba-password-again password root" | debconf-set-selections
echo "virtuoso-opensource-7.1 virtuoso-opensource-7.1/dba-password password root" | debconf-set-selections

#################################################################
apt-get -y update --force-yes
#################################################################
# Change the default homepage

echo "127.0.0.1 mapping.semic.eu" >> /etc/hosts
echo "user_pref(\"browser.startup.homepage\", \"http://mapping.semic.eu\");" >> /etc/firefox/syspref.js
echo "_user_pref(\"browser.startup.homepage\", \"http://mapping.semic.eu\");" >> /etc/firefox/browser/defaults/preferences/syspref.js
echo "user_pref(\"browser.startup.ghomepage\", \"http://mapping.semic.eu\");" >> /etc/iceweasel/pref/iceweasel.js
echo "_user_pref(\"browser.startup.homepage\", \"http://mapping.semic.eu\");" >> /etc/iceweasel/profile/prefs.js

echo "*********** done with main bootstrap creation  ***********"
apt-get autoclean
echo "*********** done with bootstrap of dev machine ***********"
#################################################################

