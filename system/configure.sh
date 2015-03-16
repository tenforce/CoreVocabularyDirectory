#!/bin/sh
# Configuration script
#
# Copyright 2014 European Union
# Author: Vianney le Clément de Saint-Marcq (PwC EU Services)
#
# Licensed under the EUPL, Version 1.1 or - as soon they
# will be approved by the European Commission - subsequent
# versions of the EUPL (the "Licence");
# You may not use this work except in compliance with the
# Licence.
# You may obtain a copy of the Licence at:
# http://ec.europa.eu/idabc/eupl
#
# Unless required by applicable law or agreed to in
# writing, software distributed under the Licence is
# distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.
# See the Licence for the specific language governing
# permissions and limitations under the Licence.

set -e -u

# Default values
IP=vocabs.tenforce.com
#IP=188.64.53.147
BASEURI="http://${IP}/vdm/"
ROOTURI="file://vdm/"
DEFAULT_GRAPH="http://${IP}/DAV"
GOOGLE_ANALYTICS="UA-38243808-1"

GENERATE=true

# Usage notice
usage() {
    cat <<EOF
Usage: $0 [options]

Options:
  -b URI    The base URI (default: ${BASEURI})
  -r URI    The (internal) URI of the root directory
              (default: ${ROOTURI})
  -g URI    Default graph URI for SPARQL queries
              (default: ${DEFAULT_GRAPH})
  -a KEY    Google Analytics key (default: ${GOOGLE_ANALYTICS})
  -c        Remove generated files
  -h        This help screen
EOF
}

# Parse arguments
while getopts 'b:r:g:a:ch' opt; do
    case "${opt}" in
    b) BASEURI=${OPTARG%/}/ ;;
    r) ROOTURI=${OPTARG%/}/ ;;
    g) DEFAULT_GRAPH=${OPTARG} ;;
    a) GOOGLE_ANALYTICS=${OPTARG} ;;
    c) GENERATE=false ;;
    h) usage ; exit 0 ;;
    *) usage ; exit 1 ;;
    esac
done

# Construct sed replacement script
sed=""
for var in BASEURI ROOTURI DEFAULT_GRAPH GOOGLE_ANALYTICS; do
    eval "value=\$${var}"
    sed="${sed}s|%${var}%|${value}|g;"
done

# Generate files
find -name '*.in' |
while read -r infile; do
    outfile=${infile%.in}
    if ${GENERATE}; then
        printf 'Writing %s\n' "${outfile}"
        cat "${infile}" | sed "${sed}" > "${outfile}"
    elif [ -e "${outfile}" ]; then
        printf 'Removing %s\n' "${outfile}"
        rm "${outfile}"
    fi
done
