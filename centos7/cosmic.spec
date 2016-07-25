# DISABLE the post-percentinstall java repacking and line number stripping
# we need to find a way to just disable the java repacking and line number stripping, but not the autodeps
%define __os_install_post %{nil}
%global debug_package %{nil}

Name:      cosmic
Summary:   Cosmic IaaS Platform
#http://fedoraproject.org/wiki/PackageNamingGuidelines#Pre-Release_packages
%if "%{?_prerelease}" != ""
%define _maventag %{_ver}-SNAPSHOT
Release:   %{_rel}%{dist}
%else
%define _maventag %{_ver}
Release:   %{_rel}%{dist}
%endif

%{!?python_sitearch: %define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}

Version:   %{_ver}
License:   ASL 2.0
Vendor:    Cosmic <int-cloud@schubergphilis.com>
Packager:  Cosmic <int-cloud@schubergphilis.com>
Group:     System Environment/Libraries
Source0:   %{name}-%{_maventag}.tgz
BuildRoot: %{_tmppath}/%{name}-%{_maventag}-%{release}-build

%description
Cosmic is a highly-scalable elastic, open source,
intelligent IaaS cloud implementation.


#############################
# COMMON PACKAGE            #
#############################

%package common
Summary: Cosmic common files and scripts
Requires: python
Group:   System Environment/Libraries

%description common
The Cosmic files shared between agent and management server


############################
# AGENT PACKAGE            #
############################

%package agent
Summary: Cosmic Agent for KVM hypervisors
Requires: openssh-clients
Requires: java => 1.8.0
Requires: %{name}-common = %{_ver}
Requires: libvirt
Requires: bridge-utils
Requires: ebtables
Requires: iptables
Requires: ethtool
Requires: iproute
Requires: ipset
Requires: perl
Requires: libvirt-python
Requires: qemu-img
Requires: qemu-kvm
Requires: socat
Provides: cloud-agent
Group: System Environment/Libraries

%description agent
The Cosmic agent for KVM hypervisors

%prep
%setup -q -n %{name}-%{_maventag}
%build

%install
[ ${RPM_BUILD_ROOT} != "/" ] && rm -rf ${RPM_BUILD_ROOT}

# Common directories
mkdir -p ${RPM_BUILD_ROOT}%{_bindir}
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/log/%{name}/agent
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/log/%{name}/ipallocator
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/%{name}/mnt
mkdir -p ${RPM_BUILD_ROOT}%{_initrddir}
mkdir -p ${RPM_BUILD_ROOT}%{_sysconfdir}/sysconfig
mkdir -p ${RPM_BUILD_ROOT}%{_sysconfdir}/profile.d
mkdir -p ${RPM_BUILD_ROOT}%{_sysconfdir}/sudoers.d

# Common
mkdir -p ${RPM_BUILD_ROOT}%{_datadir}/%{name}-common/scripts
mkdir -p ${RPM_BUILD_ROOT}%{_datadir}/%{name}-common/vms
mkdir -p ${RPM_BUILD_ROOT}%{python_sitearch}/
mkdir -p ${RPM_BUILD_ROOT}%/usr/bin
cp -r      %{_sourcecodefolder}/cosmic-core/scripts/* ${RPM_BUILD_ROOT}%{_datadir}/%{name}-common/scripts
install -D %{_sourcecodefolder}/cosmic-core/systemvm/dist/systemvm.iso ${RPM_BUILD_ROOT}%{_datadir}/%{name}-common/vms/systemvm.iso
install    %{_sourcecodefolder}/cosmic-core/python/lib/cloud_utils.py ${RPM_BUILD_ROOT}%{python_sitearch}/cloud_utils.py
cp -r      %{_sourcecodefolder}/cosmic-core/python/lib/cloudutils ${RPM_BUILD_ROOT}%{python_sitearch}/
python -m py_compile ${RPM_BUILD_ROOT}%{python_sitearch}/cloud_utils.py
python -m compileall ${RPM_BUILD_ROOT}%{python_sitearch}/cloudutils

install -D %{_sourcecodefolder}/cosmic-client/target/pythonlibs/jasypt-1.9.2.jar ${RPM_BUILD_ROOT}%{_datadir}/%{name}-common/lib/jasypt-1.9.2.jar

chmod 770 ${RPM_BUILD_ROOT}%{_localstatedir}/log/%{name}/agent

# KVM Agent
mkdir -p ${RPM_BUILD_ROOT}%{_sysconfdir}/%{name}/agent
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/log/%{name}/agent
mkdir -p ${RPM_BUILD_ROOT}%{_datadir}/%{name}-agent/lib
mkdir -p ${RPM_BUILD_ROOT}%{_datadir}/%{name}-agent/plugins
install -D %{_packagefolder}/systemd/cosmic-agent.service ${RPM_BUILD_ROOT}%{_unitdir}/%{name}-agent.service
install -D %{_sourcecodefolder}/cosmic-agent/target/transformed/agent.properties ${RPM_BUILD_ROOT}%{_sysconfdir}/%{name}/agent/agent.properties
install -D %{_sourcecodefolder}/cosmic-agent/target/transformed/environment.properties ${RPM_BUILD_ROOT}%{_sysconfdir}/%{name}/agent/environment.properties
install -D %{_sourcecodefolder}/cosmic-agent/target/transformed/cloud-setup-agent ${RPM_BUILD_ROOT}%{_bindir}/%{name}-setup-agent
install -D %{_sourcecodefolder}/cosmic-agent/target/transformed/cosmic-agent-upgrade ${RPM_BUILD_ROOT}%{_bindir}/%{name}-agent-upgrade
install -D %{_sourcecodefolder}/cosmic-agent/target/transformed/libvirtqemuhook ${RPM_BUILD_ROOT}%{_datadir}/%{name}-agent/lib/libvirtqemuhook
install -D %{_sourcecodefolder}/cosmic-agent/target/transformed/cloud-ssh ${RPM_BUILD_ROOT}%{_bindir}/%{name}-ssh
install -D %{_sourcecodefolder}/cosmic-agent/target/transformed/cosmic-agent-profile.sh ${RPM_BUILD_ROOT}%{_sysconfdir}/profile.d/%{name}-agent-profile.sh
install -D %{_sourcecodefolder}/cosmic-agent/target/transformed/cosmic-agent.logrotate ${RPM_BUILD_ROOT}%{_sysconfdir}/logrotate.d/%{name}-agent
install -D %{_sourcecodefolder}/cosmic-core/plugins/hypervisor/kvm/target/cloud-plugin-hypervisor-kvm-%{_maventag}.jar ${RPM_BUILD_ROOT}%{_datadir}/%name-agent/lib/cloud-plugin-hypervisor-kvm-%{_maventag}.jar

cp      %{_sourcecodefolder}/cosmic-core/plugins/hypervisor/kvm/target/dependencies/*  ${RPM_BUILD_ROOT}%{_datadir}/%{name}-agent/lib
cp      %{_sourcecodefolder}/cosmic-agent/target/dependencies/*  ${RPM_BUILD_ROOT}%{_datadir}/%{name}-agent/lib

# No scripts should be present in the Agent cloud-nucleo jar; otherwise we might face classpath order problems.
zip    -d ${RPM_BUILD_ROOT}%{_datadir}/%{name}-agent/lib/cloud-nucleo-%{_maventag}.jar scripts*

%clean
[ ${RPM_BUILD_ROOT} != "/" ] && rm -rf ${RPM_BUILD_ROOT}


#######################################
# AGENT PACKAGE (UN)INSTALL           #
#######################################

%preun agent
/sbin/service cosmic-agent stop || true
if [ "$1" == "0" ] ; then
    /sbin/chkconfig --del comsic-agent > /dev/null 2>&1 || true
fi

%pre agent
# save old configs if they exist (for upgrade). Otherwise we may lose them
# when the old packages are erased. There are a lot of properties files here.
if [ -d "%{_sysconfdir}/cloud" ] ; then
    mv %{_sysconfdir}/cloud %{_sysconfdir}/cloud.rpmsave
fi

%post agent
if [ "$1" == "1" ] ; then
    echo "Running %{_bindir}/%{name}-agent-upgrade to update bridge name for upgrade from Cosmic 4.0.x (and before) to Cosmic 4.1 (and later)"
    %{_bindir}/%{name}-agent-upgrade
    if [ ! -d %{_sysconfdir}/libvirt/hooks ] ; then
        mkdir %{_sysconfdir}/libvirt/hooks
    fi
    cp -a ${RPM_BUILD_ROOT}%{_datadir}/%{name}-agent/lib/libvirtqemuhook %{_sysconfdir}/libvirt/hooks/qemu
    /sbin/service libvirtd restart
    /sbin/systemctl enable cosmic-agent > /dev/null 2>&1 || true
fi

# if saved configs from upgrade exist, copy them over
if [ -f "%{_sysconfdir}/cloud.rpmsave/agent/agent.properties" ]; then
    mv %{_sysconfdir}/%{name}/agent/agent.properties  %{_sysconfdir}/%{name}/agent/agent.properties.rpmnew
    cp -p %{_sysconfdir}/cloud.rpmsave/agent/agent.properties %{_sysconfdir}/%{name}/agent
    # make sure we only do this on the first install of this RPM, don't want to overwrite on a reinstall
    mv %{_sysconfdir}/cloud.rpmsave/agent/agent.properties %{_sysconfdir}/cloud.rpmsave/agent/agent.properties.rpmsave
fi


#################################
# COMMON PACKAGE FILES          #
#################################

%files common
%dir %attr(0755,root,root) %{python_sitearch}/cloudutils
%dir %attr(0755,root,root) %{_datadir}/%{name}-common/vms
%attr(0755,root,root) %{_datadir}/%{name}-common/scripts
%attr(0644, root, root) %{_datadir}/%{name}-common/vms/systemvm.iso
%attr(0644,root,root) %{python_sitearch}/cloud_utils.py
%attr(0644,root,root) %{python_sitearch}/cloud_utils.pyc
%attr(0644,root,root) %{python_sitearch}/cloudutils/*
%attr(0644, root, root) %{_datadir}/%{name}-common/lib/jasypt-1.9.2.jar


#################################
# AGENT PACKAGE FILES           #
#################################

%files agent
%attr(0755,root,root) %{_bindir}/%{name}-setup-agent
%attr(0755,root,root) %{_bindir}/%{name}-agent-upgrade
%attr(0755,root,root) %{_bindir}/%{name}-ssh
%attr(0644,root,root) %{_unitdir}/%{name}-agent.service
%attr(0644,root,root) %{_sysconfdir}/profile.d/%{name}-agent-profile.sh
%attr(0644,root,root) %{_sysconfdir}/logrotate.d/%{name}-agent
%config(noreplace) %{_sysconfdir}/%{name}/agent
%dir %{_localstatedir}/log/%{name}/agent
%attr(0644,root,root) %{_datadir}/%{name}-agent/lib/*.jar
%attr(0755,root,root) %{_datadir}/%{name}-agent/lib/libvirtqemuhook
%dir %{_datadir}/%{name}-agent/plugins
