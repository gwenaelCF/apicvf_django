#!/bin/bash
# gitlab-ci-script.sh [options]
# by default run testu + sonar
# with --testu_sonar, run testu + sonar
# with --build, run only the build

GIT_BASE="/builds/apic/"
PLUGIN_NAME="apicvf_django"
PLUGIN_RUNTIME="/home/mfserv/var/plugins/${PLUGIN_NAME}"

install_locale()
{
    echo "-> Install locale fr_FR.UTF-8"
    /usr/bin/sudo -n yum reinstall glibc-common
    localedef -c -i fr_FR -f UTF-8 fr_FR.UTF-8
    echo "LANG=fr_FR.ISO-8859-15" > /etc/locale.conf
}

prepare()
{
    install_locale
    # start mfserv
    echo "-> 1. Start mfserv"
    mfserv.start
}

make_release()
{
    # make relase
	echo "-> 2.Make release"
	make release
}

install()
{
	# install plugin
	echo "-> 3. Install plugin"
	plugins.install apicvf_django-*.metwork.mfserv.plugin
}

testu()
{
    # start mfserv
    prepare
    # make release
    make_release
    # install plugin
    install

    # edit settings.py
    cd ${PLUGIN_RUNTIME}/${PLUGIN_NAME}
    sed -i "s/'HOST':.*/'HOST': 'postgres',/" settings.py
    sed -i "s/'PORT':.*/'PORT': '5432',/" settings.py
    sleep 10
    
    # launch tests + coverage
    cd ${PLUGIN_RUNTIME}
    echo "-> A. Launch test (through coverage)"
    plugin_wrapper ${PLUGIN_NAME} -- coverage run --source='apicvf_django','epistola','procedere','carto','parameters' manage.py test
    echo "-> B. Launch coverage xml report, and display it"
    plugin_wrapper ${PLUGIN_NAME} coverage xml
    plugin_wrapper ${PLUGIN_NAME} coverage report
    
    # Launch sonar
    sonar
}

sonar()
{
    # move to plugin installed directory
    cd ${PLUGIN_RUNTIME}
    
    # coverage - change the path of the sources to match the sources of the project
    sed -i "s#/home/mfserv/var/plugins/${PLUGIN_NAME}/##g" coverage.xml
    
    # launch sonar-scanner (add -X for debug)
    /opt/sonar-scanner/bin/sonar-scanner
    
    # extract sonar result
    export url=$(cat .scannerwork/report-task.txt | grep ceTaskUrl | cut -c11-)
    sleep 5s #Wait time for the report
    curl -k $url -o analysis.txt #store results in analysis.txt
    export status=$(cat analysis.txt | jq -r '.task.status') #Get the status as SUCCESS, CANCELED or FAILED
    export analysisId=$(cat analysis.txt | jq -r '.task.analysisId') #Get the analysis Id
    curl -k  http://sonar.meteo.fr/api/qualitygates/project_status?analysisId=$analysisId -o result.txt;
    export result=$(cat result.txt | jq -r '.projectStatus.status');
    if [ “$result” == “ERROR” ]; then echo -e 'SONAR RESULTS FAILED'; exit 1; fi
}

build()
{
    # start mfserv
    prepare
    # make release
    make_release
}

cd ${GIT_BASE}/${PLUGIN_NAME}/

case "$1" in
"--testu_sonar")
    testu
    ;;
"--build")
    build
    ;;
*)
	testu
    ;;
esac
