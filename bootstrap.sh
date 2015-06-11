#!/usr/bin/env bash
#################################################################
echo "deb http://http.debian.net/debian wheezy-backports main" >> /etc/apt/sources.list.d/wheezy-backports.list
apt-get install -t wheezy-backports linux-image-amd65
apt-get install -y ntp xinit xterm iceweasel gnome-terminal gnome-shell
apt-get install -y dkms virtualbox-guest-dkms virtualbox-guest-x11
apt-get install -y gdm3 python-software-properties software-properties-common
apt-get install -y python python3 emacs xsltproc make autoconf redland-utils
apt-get install -y rasqal-utils gawk dos2unix emacs curl
apt-get remove -y docker
dpkg-reconfigure gdm3
# Python 3 tools and some libraries which will be needed
apt-get install -y python3-setuptools
easy_install3 rdflib
easy_install3 xlrd

#################################################################
# Docker setup (docker is a different thing on wheezy), so take
# from main site.
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 36A1D7869245C8950F966E92D8576A8BA88D21E9
curl -ksSL https://get.docker.com/ | sh
groupadd docker
gpasswd -a vagrant docker

#################################################################
# Setup the extra source lists (lod2 stack and prolog)
#
apt-get update -y --force-yes

#################################################################
# Set the default values for the debconf questions
#
apt-get install -y debconf-utils
echo "virtuoso-opensource-7.1 virtuoos-opensource-7.1/dba-password-again password root" | debconf-set-selections
echo "virtuoso-opensource-7.1 virtuoso-opensource-7.1/dba-password password root" | debconf-set-selections

#################################################################
# Change the default homepage

echo "127.0.0.1 mapping.semic.eu" >> /etc/hosts
echo "user_pref(\"browser.startup.homepage\", \"http://mapping.semic.eu\");" >> /etc/firefox/syspref.js
echo "_user_pref(\"browser.startup.homepage\", \"http://mapping.semic.eu\");" >> /etc/firefox/browser/defaults/preferences/syspref.js
echo "user_pref(\"browser.startup.homepage\", \"http://mapping.semic.eu\");" >> /etc/iceweasel/pref/iceweasel.js
echo "_user_pref(\"browser.startup.homepage\", \"http://mapping.semic.eu\");" >> /etc/iceweasel/profile/prefs.js

echo "****** done with main bootstrap creation"
apt-get autoclean
echo "****** done with bootstrap of dev machine"
#################################################################

