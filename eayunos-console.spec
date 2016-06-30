%define _version 1.0
%define _release 0

Name:		eayunos-console
Version:	%{_version}
Release:	%{_release}%{?dist}
Summary:	EayunOS console

Group:		ovirt-engine-third-party
License:	GPL
URL:		http://www.eayun.com
Source0:	eayunos-console-%{_version}.tar.gz
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

%description
tui based setup and management ui for eayunos

%prep
%setup -q

%install
mkdir -p %{buildroot}/usr/lib/python2.7/site-packages
mkdir -p %{buildroot}/usr/sbin
mkdir -p %{buildroot}/etc/eayunos-console-node
mkdir -p %{buildroot}/usr/share
mv eayunos_console_node/answers.conf %{buildroot}/etc/eayunos-console-node
mv eayunos_console_node/answers_add.conf %{buildroot}/etc/eayunos-console-node
cp -r eayunos_console_node %{buildroot}/usr/lib/python2.7/site-packages
cp -r eayunos_console_common %{buildroot}/usr/lib/python2.7/site-packages
cp -r eayunos_console_manager %{buildroot}/usr/lib/python2.7/site-packages
mv %{buildroot}/usr/lib/python2.7/site-packages/eayunos_console_manager/neutron-uiplugin %{buildroot}/usr/share
cp node-console %{buildroot}/usr/sbin
cp manager-console %{buildroot}/usr/sbin

%package node
Summary:    tui based setup and management ui for eayunos host
Group:      ovirt-engine-third-party
Requires:	ovirt-engine-appliance
Requires:	ovirt-hosted-engine-setup
Requires:	vdsm
Requires:	python-urwid

%description node
tui based setup and management ui for eayunos host

%files node
%defattr(-,root,root,-)
/usr/lib/python2.7/site-packages/eayunos_console_node
/usr/lib/python2.7/site-packages/eayunos_console_common
/etc/eayunos-console-node/answers.conf
/etc/eayunos-console-node/answers_add.conf
%attr(0755,root,root) /usr/sbin/node-console

%package manager
Summary:    tui based setup and management ui for eayunos manager
Group:      ovirt-engine-third-party
Requires:       ovirt-engine
Requires:	python-urwid

%description manager
tui based setup and management ui for eayunos manager

%files manager
%defattr(-,root,root,-)
/usr/lib/python2.7/site-packages/eayunos_console_manager
/usr/lib/python2.7/site-packages/eayunos_console_common
/usr/share/neutron-uiplugin
%attr(0755,root,root) /usr/sbin/manager-console

%clean
rm -rf %{buildroot}

%changelog

* Sun May 8 2016 walteryang47 <walteryang47@gmail.com> 1.0-0
- First build

