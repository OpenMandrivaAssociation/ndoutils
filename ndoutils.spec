%define _disable_ld_no_undefined 1

%define nsusr nagios
%define nsgrp nagios
%define beta  b9

Summary:	Nagios Data Output Utilities
Name:		ndoutils
Version:	1.4
Release:	%mkrel 0.%{beta}.6
Epoch:      1
Group:		System/Servers
License:	GPL
URL:		http://www.nagios.org/
Source0:	http://downloads.sourceforge.net/nagios/ndoutils-%{version}%{beta}.tar.gz
Source1:	ndo2db.init
Patch0:		ndoutils-1.4b9-mdv-config.patch
Patch2:		ndoutils-1.4b8-no-database-prefix.patch
Requires:       nagios >= 3.0
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires(pre): rpm-helper
Requires(postun): rpm-helper
BuildRequires:	mysql-devel
BuildRequires:	postgresql-devel
BuildRequires:	nagios-devel
BuildRequires:	tcp_wrappers-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}

%description
The NDOUTILS (Nagios Data Output Utils) addon allows you to move status and
even information from Nagios to a database for later retrieval and processing.

%package common
Summary:    The part common to client and server parts
Group:		System/Servers

%description common
This package contains the part common to client and server parts.

%package client
Summary:    The client part of %{name}
Group:		System/Servers
Requires:   %{name}-common = %{epoch}:%{version}-%{release}

%description client
This package contains the client part of NDOUTILS (Nagios Data Output Utils).

%package server
Summary:    The server part of %{name}
Group:		System/Servers
Requires:   %{name}-common = %{epoch}:%{version}-%{release}

%description server
This package contains the server part of NDOUTILS (Nagios Data Output Utils).

%prep
%setup -q -n ndoutils-%{version}%{beta}
%patch0 -p1
%patch2 -p1


# lib64 fix
perl -pi -e "s|/usr/lib/|%{_libdir}/|g" config/*

%build
%serverbuild

%configure2_5x \
    --with-mysql-lib=%{_libdir}/mysql \
    --with-pgsql-lib=%{_libdir}

make

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_initrddir}
install -d %{buildroot}%{_sbindir}
install -d %{buildroot}%{_bindir}
install -d %{buildroot}%{_libdir}/nagios/brokers
install -d %{buildroot}%{_sysconfdir}/nagios
install -d %{buildroot}%{_localstatedir}/lib/ndo

install -m0755 src/ndo2db-3x %{buildroot}%{_sbindir}/ndo2db
install -m0755 src/file2sock %{buildroot}%{_bindir}/file2sock
install -m0755 src/log2ndo %{buildroot}%{_bindir}/log2ndo
install -m0755 src/sockdebug %{buildroot}%{_bindir}/sockdebug
install -m0755 src/ndomod-3x.o %{buildroot}%{_libdir}/nagios/brokers/ndomod.o
install -m0644 config/ndomod.cfg-sample \
    %{buildroot}%{_sysconfdir}/nagios/ndomod.cfg
install -m0644 config/ndo2db.cfg-sample \
    %{buildroot}%{_sysconfdir}/nagios/ndo2db.cfg
install -m0755 %{SOURCE1} %{buildroot}%{_initrddir}/ndo2db

cat > README.urpmi <<EOF
Mandriva RPM specific notes

setup
-----
The mysql database creation script has been modified to not enforce a table name
prefix by default

post-installation
-----------------
You have to:
- create a MySQL database
- create an user with at least SELECT, INSERT, UPDATE, DELETE privileges on it
- run %{_docdir}/db/mysql.sql script
EOF


%post server
%_post_service ndo2db

%preun server
%_preun_service ndo2db

%pre common
%_pre_useradd %{nsusr} /var/log/nagios /bin/sh

%postun common
%_postun_userdel %{nsusr}

%clean
rm -rf %{buildroot}

%files common
%defattr(-,root,root)
%doc db docs/* Changelog README REQUIREMENTS TODO UPGRADING
%doc config/misccommands.cfg config/nagios.cfg README.urpmi
%attr(-,%{nsusr},%{nsgrp}) %{_localstatedir}/lib/ndo

%files client
%defattr(-,root,root)
%{_bindir}/file2sock
%{_bindir}/log2ndo
%{_bindir}/sockdebug
%{_libdir}/nagios/brokers/ndomod.o
%config(noreplace) %{_sysconfdir}/nagios/ndomod.cfg

%files server
%defattr(-,root,root)
%{_initrddir}/ndo2db 
%config(noreplace) %{_sysconfdir}/nagios/ndo2db.cfg
%{_sbindir}/ndo2db


%changelog
* Thu Mar 17 2011 Oden Eriksson <oeriksson@mandriva.com> 1:1.4-0.b9.6mdv2011.0
+ Revision: 645848
- relink against libmysqlclient.so.18

* Sat Jan 01 2011 Oden Eriksson <oeriksson@mandriva.com> 1:1.4-0.b9.5mdv2011.0
+ Revision: 627266
- rebuilt against mysql-5.5.8 libs, again

* Thu Dec 30 2010 Oden Eriksson <oeriksson@mandriva.com> 1:1.4-0.b9.4mdv2011.0
+ Revision: 626547
- rebuilt against mysql-5.5.8 libs

* Mon Dec 06 2010 Oden Eriksson <oeriksson@mandriva.com> 1:1.4-0.b9.2mdv2011.0
+ Revision: 613005
- the mass rebuild of 2010.1 packages

* Mon Mar 29 2010 Guillaume Rousse <guillomovitch@mandriva.org> 1:1.4-0.b9.1mdv2010.1
+ Revision: 528815
- new version

* Thu Feb 18 2010 Oden Eriksson <oeriksson@mandriva.com> 1:1.4-0.b8.3mdv2010.1
+ Revision: 507493
- rebuild

  + Thomas Backlund <tmb@mandriva.org>
    - fix spacing in initscript

* Sun Jul 19 2009 Guillaume Rousse <guillomovitch@mandriva.org> 1:1.4-0.b8.2mdv2010.0
+ Revision: 397982
- fix dependencies for the -common package

* Sun Jul 19 2009 Guillaume Rousse <guillomovitch@mandriva.org> 1:1.4-0.b8.1mdv2010.0
+ Revision: 397489
- new version
- rediff no-database-prefix patch
- set epoch, as release tag was wrong

* Sat Dec 06 2008 Oden Eriksson <oeriksson@mandriva.com> 1.4-6.b7.6mdv2009.1
+ Revision: 311387
- fix build
- nuke P1, not needed anymore
- rebuilt against mysql-5.1.30 libs

  + Thierry Vignaud <tv@mandriva.org>
    - rebuild early 2009.0 package (before pixel changes)

  + Pixel <pixel@mandriva.com>
    - adapt to %%_localstatedir now being /var instead of /var/lib (#22312)

* Thu May 15 2008 Guillaume Rousse <guillomovitch@mandriva.org> 1.4-0.b7.5mdv2009.0
+ Revision: 207542
- delete stale socket if present when starting
- LSB headers in initscript

* Thu Feb 14 2008 Oden Eriksson <oeriksson@mandriva.com> 1.4-0.b7.4mdv2008.1
+ Revision: 168650
- try to build it without the %%make macro
- rebuild

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

* Wed Dec 19 2007 Guillaume Rousse <guillomovitch@mandriva.org> 1.4-0.b7.3mdv2008.1
+ Revision: 133918
- no duplication of file perms in %%file section
- avoid useless intermediate copy of additional sources
- patch2: don't use prefix by default for database table names
  add README.urpmi

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Mon Dec 17 2007 Guillaume Rousse <guillomovitch@mandriva.org> 1.4-0.b7.2mdv2008.1
+ Revision: 124217
- rediff configuration patch to fix log file location

* Mon Dec 17 2007 Guillaume Rousse <guillomovitch@mandriva.org> 1.4-0.b7.1mdv2008.1
+ Revision: 121724
- new version

* Fri Oct 12 2007 Oden Eriksson <oeriksson@mandriva.com> 1.4-0.b6.1mdv2008.1
+ Revision: 97496
- import ndoutils


* Fri Oct 12 2007 Oden Eriksson <oeriksson@mandriva.com> 1.4-0.b6.1mdv2008.0
- initial Mandriva package
