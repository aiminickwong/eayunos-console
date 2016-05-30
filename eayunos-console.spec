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
mv eayunos_console_node/answers.conf %{buildroot}/etc/eayunos-console-node
cp -r eayunos_console_node %{buildroot}/usr/lib/python2.7/site-packages
cp -r eayunos_console_common %{buildroot}/usr/lib/python2.7/site-packages
cp node-console %{buildroot}/usr/sbin

%package node
Summary:    tui based setup and management ui for eayunos host
Group:      ovirt-engine-third-party
Requires:	ovirt-engine-appliance
Requires:	ovirt-hosted-engine-setup
Requires:	vdsm

%description node
tui based setup and management ui for eayunos host

%clean node
rm -rf %{buildroot}

%files node
%defattr(-,root,root,-)
/usr/lib/python2.7/site-packages/eayunos_console_node
/usr/lib/python2.7/site-packages/eayunos_console_common
/etc/eayunos-console-node/answers.conf
%attr(0755,root,root) /usr/sbin/node-console

%changelog

* Sun May 8 2016 walteryang47 <walteryang47@gmail.com> 1.0-0
- First build

