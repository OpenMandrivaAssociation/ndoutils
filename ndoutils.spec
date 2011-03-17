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
