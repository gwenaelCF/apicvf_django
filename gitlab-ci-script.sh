#!/bin/bash
# gitlab-ci-script.sh [options]
# by default run testu
# with --testu, run only the testu

GIT_BASE="/builds/apic/"
PLUGIN_NAME="apicvf_django"
PLUGIN_RUNTIME="/home/mfserv/var/plugins/${PLUGIN_NAME}"

install()
{
    # start mfserv
    echo "-> 1. Start mfsev"
    mfserv.start
	# make relase
	echo "-> 2.Make release"
	make release
	# install plugin
	echo "-> 3. Install plugin"
	plugins.install apicvf_django-*.metwork.mfserv.plugin
}

testu()
{
    # install plugin
    install

    cd ${PLUGIN_RUNTIME}
    echo "-> A. Launch test (through coverage)"
    plugin_wrapper ${PLUGIN_NAME} coverage run manage.py test carto.tests
    echo "-> B. Launch coverage xml report"
    plugin_wrapper ${PLUGIN_NAME} coverage xml
}

cd ${GIT_BASE}/${PLUGIN_NAME}/

case "$1" in
"--testu")
    testu
    ;;
*)
	testu
    ;;
esac
