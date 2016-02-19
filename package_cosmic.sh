#!/bin/bash

function usage() {
    echo ""
    echo "usage: ./package.sh [-h|--help] -d|--distribution <name> [-r|--release <version>] [-p|--package <name[,name,...]>] [-f|--folder <name>] [-b|--build <[options]>"
    echo ""
    echo "The supported arguments are:"
    echo "  To build a package for a distribution (mandatory)"
    echo "    -d|--distribution centos7"
    echo ""
    echo "  To set the package release version (optional)"
    echo "  (default is 1 for normal and prereleases, empty for SNAPSHOT)"
    echo "    -r|--release version(integer)"
    echo ""
    echo "  To select the package to be build"
    echo "  (default is none, if not specified every package is build)"
    echo "    -p|--package name[,name,...]"
    echo ""
    echo "  To select the source code folder"
    echo "  (if not specified parent dir is used)"
    echo "    -f|--folder name"
    echo ""
    echo "  Run -- mvn clean package -Psystemvm -- before packaging"
    echo "    -b|--build options"
    echo ""
    echo "  To display this information"
    echo "    -h|--help"
    echo ""
    echo "Examples: ./package.sh -d centos7"
    echo "          ./package.sh -d centos7 -r 42"
    echo "          ./package.sh -d centos7 -r 42"
    echo "          ./package.sh -d centos7 -p common,agent"
}

# absolute path
#  $1 path
function abspath() {
    local  __resultvar=$1
    ABS_PATH=`cd "$__resultvar"; pwd`
    eval $__resultvar="$ABS_PATH"
}

# package
#  $1 PACKAGES
#  $2 TARGETDISTRO
#  $3 RELEASE
#  $4 SOURCECODEFOLDER <PATH>
#  $5 BUILD
#  $6 PACKAGEPATH <PATH>
#  $7 PROJECTNAME
#  $8 BUILDOPTIONS
function package() {
    PACKAGES="$1"
    TARGETDISTRO="$2"
    RELEASE="$3"
    SOURCECODEFOLDER=`cd "$4"; pwd`
    BUILD="$5"
    PACKAGEPATH=`cd "$6"; pwd`
    PROJECTNAME="$7"
    BUILDOPTIONS="$8"

    RPMDIR="$PACKAGEPATH/dist/rpmbuild"
    TARGETDISTROPATH="$PACKAGEPATH/$TARGETDISTRO"

    MVN=$(which mvn)
    if [ -z "$MVN" ] ; then
        MVN=$(locate bin/mvn | grep -e mvn$ | tail -1)
        if [ -z "$MVN" ] ; then
            echo -e "mvn not found\n cannot retrieve version to package\n RPM Build Failed"
            exit 2
        fi
    fi
    VERSION=$(cd $SOURCECODEFOLDER; $MVN org.apache.maven.plugins:maven-help-plugin:2.1.1:evaluate -Dexpression=project.version | grep --color=none '^[0-9]\.')

    if echo "$VERSION" | grep -q SNAPSHOT ; then
        REALVER=$(echo "$VERSION" | cut -d '-' -f 1)
        if [ -n "$RELEASE" ] ; then
            DEFPRE="-D_prerelease $RELEASE"
            DEFREL="-D_rel SNAPSHOT$RELEASE"
        else
            DEFPRE="-D_prerelease 1"
            DEFREL="-D_rel SNAPSHOT"
        fi
    else
        REALVER="$VERSION"
        if [ -n "$RELEASE" ] ; then
            DEFREL="-D_rel $RELEASE"
        else
            DEFREL="-D_rel 1"
        fi
    fi
    DEFVER="-D_ver $REALVER"
    DEFSOURCECODEFOLDER="-D_sourcecodefolder ${SOURCECODEFOLDER}"
    DEFPACKAGEFOLDER="-D_packagefolder ${PACKAGEPATH}"
    DEFTMPFOLDER="-D_tmppath ${RPMDIR}"
    DEFTOPDIR="-D_topdir ${RPMDIR}"

    echo "[INFO] Creating rpmbuild directory structure"

    mkdir -p "$RPMDIR/SPECS"
    mkdir -p "$RPMDIR/BUILD"
    mkdir -p "$RPMDIR/RPMS"
    mkdir -p "$RPMDIR/SRPMS"
    mkdir -p "$RPMDIR/SOURCES"

    echo "[INFO] Creating source code tar (from $SOURCECODEFOLDER)"
    PACKAGE_NAME=${PROJECTNAME}-${VERSION}
    (cd $SOURCECODEFOLDER/..; ln -s $SOURCECODEFOLDER $PACKAGE_NAME; tar -czhf "$RPMDIR/SOURCES/$PACKAGE_NAME.tgz" --exclude .git $PACKAGE_NAME; rm -f $PACKAGE_NAME)

    cp "$TARGETDISTROPATH/cosmic.spec" "$RPMDIR/SPECS"

    if [ "$BUILD" = "true" ]; then
        echo "[INFO] Compiling source code => mvn clean package -Psystemvm $BUILDOPTIONS"
        echo ""
        (cd $SOURCECODEFOLDER; mvn clean package -Psystemvm "$BUILDOPTIONS")
    fi

    (cd "$RPMDIR"; rpmbuild "${DEFTOPDIR}" "${DEFSOURCECODEFOLDER}" "${DEFPACKAGEFOLDER}" "${DEFTMPFOLDER}" "${DEFVER}" "${DEFREL}" "${DEFPRE}" -bb SPECS/cosmic.spec)
    if [ $? -ne 0 ]; then
        echo "RPM Build Failed "
        exit 3
    else
        echo "RPM Build Done"
    fi
    exit
}

PACKAGES=""
TARGETDISTRO=""
RELEASE=""
SOURCECODEFOLDER=""
PACKAGEPATH="$(dirname $0)"
BUILD="false"
BUILDOPTIONS=""
PROJECTNAME="cosmic"

SHORTOPTS="hp:d:r:f:b:"
LONGOPTS="help,package:distribution:release:folder:build:"
ARGS=$(getopt -s bash -u -a --options "$SHORTOPTS"  --longoptions "$LONGOPTS" --name "$0" -- "$@")
eval set -- "$ARGS"
while [ $# -gt 0 ] ; do
    case "$1" in
        -h | --help)
            usage
            exit 0
            ;;
        -p | --package)
            PACKAGES=$2
			if [ -z "$PACKAGES" ] ; then
				echo "[ERROR] No package defined"
                usage
                exit 1
            fi
            echo "[INFO] Selected the following packages: $PACKAGES"
            shift
            ;;
        -d | --distribution)
            TARGETDISTRO=$2
            if [ -z "$TARGETDISTRO" ] ; then
                echo "[ERROR] Missing target distribution"
                usage
                exit 1
            fi
            echo "[INFO] Selected target distribution $TARGETDISTRO"
            shift
            ;;
        -r | --release)
            RELEASE=$2
            if [ -z "$RELEASE" ] ; then
                echo "[ERROR] Missing release number"
                usage
                exit 1
            fi
            echo "[INFO] Selected release version $RELEASE"
            shift
            ;;
        -f | --folder)
            SOURCECODEFOLDER=$2
            if [ -z "$SOURCECODEFOLDER" ] ; then
                echo "[ERROR] Source code folder not specified"
                usage
                exit 1
            fi
            echo "[INFO] Selected source code folder $SOURCECODEFOLDER"
            shift
            ;;
        -b | --build)
            BUILD="true"
            BUILDOPTIONS=$2
            echo "[INFO] Build before package"
            if [ -n "$BUILDOPTIONS" ] ; then
                echo "[INFO] Build options specified: $BUILDOPTIONS"
            fi
            shift
            ;;
        -)
            echo "[ERROR] Unrecognized option"
            usage
            exit 1
            ;;
        *)
            shift
            ;;
    esac
done

if [ -z "$TARGETDISTRO" ] ; then
    echo "[ERROR] Missing target distribution"
    usage
    exit 1
fi

if [ -z "$SOURCECODEFOLDER" ] ; then
    echo "[ERROR] Missing source code folder"
    usage
    exit 1
fi

echo ""

package "$PACKAGES" "$TARGETDISTRO" "$RELEASE" "$SOURCECODEFOLDER" "$BUILD" "$PACKAGEPATH" "$PROJECTNAME" "$BUILDOPTIONS"
