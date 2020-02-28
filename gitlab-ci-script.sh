#!/bin/bash
# gitlab-ci-script.sh [options]
# by default run testu
# with --testu, run only the testu

GIT_BASE="/builds/apic/apicvf_django"
PLUGIN_VERSION="apicvf_django"
PLUGIN_RUNTIME="/home/mfserv/var/plugins/${PLUGIN_VERSION}"

install()
{
    # start mfserv
	mfserv.start
	# make relase
	make release
	# install plugin
	plugins.install apicvf_django-*.metwork.mfserv.plugin
}

testu()
{
    install

    cd ${PLUGIN_RUNTIME}
    coverage run --source='carto' manage.py test carto.tests --keepdb
    coverage xml
}

cd ${GIT_BASE}/plugin/${PLUGIN_VERSION}/

case "$1" in
"--testu")
    testu
    ;;
*)
	testu
    ;;
esac
