%define _disable_ld_no_undefined 1

%define nsusr nagios
%define nsgrp nagios
%define beta  b7

Summary:	Nagios Data Output Utilities
Name:		ndoutils
Version:	1.4
Release:	%mkrel 6.%{beta}.6
Group:		System/Servers
License:	GPL
URL:		http://www.nagios.org/
Source0:	http://downloads.sourceforge.net/nagios/ndoutils-%{version}%{beta}.tar.gz
Source1:	ndo2db.init
Patch0:		ndoutils-mdv_conf.diff
Patch2:		ndoutils-1.4b7-no-database-prefix.patch
Requires:       nagios >= 3.0
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires(pre): rpm-helper
Requires(postun): rpm-helper
BuildRequires:	mysql-devel
BuildRequires:	postgresql-devel
BuildRequires:	nagios-devel
BuildRequires:	tcp_wrappers-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root

%description
The NDOUTILS (Nagios Data Output Utils) addon allows you to move status and
even information from Nagios to a database for later retrieval and processing.

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
install -m0644 config/ndomod.cfg %{buildroot}%{_sysconfdir}/nagios/ndomod.cfg
install -m0644 config/ndo2db.cfg %{buildroot}%{_sysconfdir}/nagios/ndo2db.cfg
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


%post
%_post_service ndo2db

%preun
%_preun_service ndo2db

%pre
%_pre_useradd %{nsusr} /var/log/nagios /bin/sh

%postun
%_postun_userdel %{nsusr}

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc db docs/* Changelog README REQUIREMENTS TODO UPGRADING
%doc config/misccommands.cfg config/nagios.cfg README.urpmi
%{_initrddir}/ndo2db 
%config(noreplace) %{_sysconfdir}/nagios/ndomod.cfg
%config(noreplace) %{_sysconfdir}/nagios/ndo2db.cfg
%{_bindir}/file2sock
%{_bindir}/log2ndo
%{_bindir}/sockdebug
%{_sbindir}/ndo2db
%{_libdir}/nagios/brokers/ndomod.o
%attr(-,%{nsusr},%{nsgrp}) %{_localstatedir}/lib/ndo

