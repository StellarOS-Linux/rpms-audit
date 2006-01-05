Summary: User space tools for 2.6 kernel auditing.
Name: audit
Version: 1.1.3
Release: 1
License: GPL
Group: System Environment/Daemons
URL: http://people.redhat.com/sgrubb/audit/
Source0: %{name}-%{version}.tar.gz
Patch1: audit-1.1.3-initscript-disabled.patch
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildRequires: libtool swig
BuildRequires: glibc-kernheaders >= 2.4-9.1.95
BuildRequires: automake >= 1.9
BuildRequires: autoconf >= 2.59
Requires: %{name}-libs = %{version}-%{release}
Requires: chkconfig

%description
The audit package contains the user space utilities for
storing and searching the audit records generate by
the audit subsystem in the Linux 2.6 kernel.

%package libs
Summary: Dynamic library for libaudit
License: LGPL
Group: Development/Libraries

%description libs
The audit-libs package contains the dynamic libraries needed for 
applications to use the audit framework.

%package libs-devel
Summary: Header files and static library for libaudit
License: LGPL
Group: Development/Libraries
Requires: %{name}-libs = %{version}-%{release}
Requires: glibc-kernheaders >= 2.4-9.1.95

%description libs-devel
The audit-libs-devel package contains the static libraries and header 
files needed for developing applications that need to use the audit 
framework libraries.

%package libs-python
Summary: Python bindings for libaudit
License: LGPL
Group: Development/Libraries
Requires: %{name}-libs = %{version}-%{release}
Requires: glibc-kernheaders >= 2.4-9.1.95

%description libs-python
The audit-libs-python package contains the bindings so that libaudit
can be used by python.

%prep
%setup -q
# When in production, uncomment this so the patch is applied
#%patch1 -p1

%build
autoreconf -fv --install
export CFLAGS="$RPM_OPT_FLAGS"
%configure --sbindir=/sbin --libdir=/%{_lib}
make

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/{sbin,etc/{sysconfig,rc.d/init.d}}
mkdir -p $RPM_BUILD_ROOT/%{_mandir}/man8
mkdir -p $RPM_BUILD_ROOT/%{_lib}
mkdir -p $RPM_BUILD_ROOT/%{_var}/log/audit
make DESTDIR=$RPM_BUILD_ROOT install

mkdir -p $RPM_BUILD_ROOT/%{_includedir}
mkdir -p $RPM_BUILD_ROOT/%{_libdir}
# We manually install this since Makefile doesn't
install -m 0644 lib/libaudit.h $RPM_BUILD_ROOT/%{_includedir}
# This winds up in the wrong place when libtool is involved
mv $RPM_BUILD_ROOT/%{_lib}/libaudit.a $RPM_BUILD_ROOT%{_libdir}
curdir=`pwd`
cd $RPM_BUILD_ROOT/%{_libdir}
LIBNAME=`basename \`ls $RPM_BUILD_ROOT/%{_lib}/libaudit.so.*.*.*\``
ln -s ../../%{_lib}/$LIBNAME libaudit.so
cd $curdir
# Remove these items so they don't get picked up.
rm -f $RPM_BUILD_ROOT/%{_lib}/libaudit.so
rm -f $RPM_BUILD_ROOT/%{_lib}/libaudit.la
rm -f $RPM_BUILD_ROOT/%{_libdir}/python2.4/site-packages/_audit.a
rm -f $RPM_BUILD_ROOT/%{_libdir}/python2.4/site-packages/_audit.la
# Temp remove this file
rm -f $RPM_BUILD_ROOT/sbin/audispd

%clean
rm -rf $RPM_BUILD_ROOT

%post libs -p /sbin/ldconfig

%post
/sbin/chkconfig --add auditd

%preun
if [ $1 -eq 0 ]; then
   /sbin/service auditd stop > /dev/null 2>&1
   /sbin/chkconfig --del auditd
fi

%postun libs
/sbin/ldconfig 2>/dev/null

%postun
if [ $1 -ge 1 ]; then
   /sbin/service auditd condrestart > /dev/null 2>&1 || :
fi

%files libs
%defattr(-,root,root)
%attr(755,root,root) /%{_lib}/libaudit.*

%files libs-devel
%defattr(-,root,root)
%{_libdir}/libaudit.a
%{_libdir}/libaudit.so
%{_includedir}/libaudit.h
%{_mandir}/man3/*

%files libs-python
%defattr(-,root,root)
%{_libdir}/python2.4/site-packages/_audit.so
/usr/lib/python2.4/site-packages/audit.py*

%files
%defattr(-,root,root,-)
%doc  README COPYING ChangeLog sample.rules contrib/capp.rules contrib/lspp.rules contrib/skeleton.c init.d/auditd.cron
%attr(0644,root,root) %{_mandir}/man8/*
%attr(750,root,root) /sbin/auditctl
%attr(750,root,root) /sbin/auditd
%attr(750,root,root) /sbin/ausearch
%attr(750,root,root) /sbin/aureport
%attr(750,root,root) /sbin/autrace
#%attr(750,root,root) /sbin/audispd
%attr(755,root,root) /etc/rc.d/init.d/auditd
%attr(750,root,root) %{_var}/log/audit
%config(noreplace) %attr(640,root,root) /etc/auditd.conf
%config(noreplace) %attr(640,root,root) /etc/audit.rules
%config(noreplace) %attr(640,root,root) /etc/sysconfig/auditd


%changelog
* Thu Jan 5 2006 Steve Grubb <sgrubb@redhat.com> 1.1.3-1
- Add timestamp to daemon_config messages (#174865)
- Add error checking of year for aureport & ausearh
- Treat af_unix sockets as files for searching and reporting
- Update capp & lspp rules to combine syscalls for higher performance
- Adjusted the chkconfig line for auditd to start a little earlier
- Added skeleton program to docs for people to write their own dispatcher with
- Apply patch from Ulrich Drepper that optimizes resource utilization
- Change ausearch and aureport to unlocked IO

* Thu Dec 5 2005 Steve Grubb <sgrubb@redhat.com> 1.1.2-1
- Add more message types

* Wed Nov 30 2005 Steve Grubb <sgrubb@redhat.com> 1.1.1-1
- Add support for alpha processors
- Update the audisp code
- Add locale code in ausearch and aureport
- Add new rule operator patch
- Add exclude filter patch
- Cleanup make files
- Add python bindings

* Wed Nov 9 2005 Steve Grubb <sgrubb@redhat.com> 1.1-1
- Add initial version of audisp. Just a placeholder at this point
- Remove -t from auditctl

* Mon Nov 7 2005 Steve Grubb <sgrubb@redhat.com> 1.0.12-1
- Add 2 more summary reports
- Add 2 more message types

