%{!?python_sitearch: %define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

# Do we want systemd?
%define WITH_SYSTEMD 1
# %define snapshot .svn20140803

Summary: User space tools for 2.6 kernel auditing
Name: audit
Version: 2.4.3
Release: 1%{?dist}
License: GPLv2+
Group: System Environment/Daemons
URL: http://people.redhat.com/sgrubb/audit/
Source0: http://people.redhat.com/sgrubb/audit/%{name}-%{version}.tar.gz
Source1: https://www.gnu.org/licenses/lgpl-2.1.txt
# FESCO asked for audit to be off by default. #1117953
Patch1: never-audit.patch

BuildRequires: swig python-devel
%ifnarch aarch64 %{power64} s390 s390x
BuildRequires: golang
# Temporary fix for make check in golang. Needs libaudit.so
BuildRequires: audit-libs-devel
%endif
BuildRequires: tcp_wrappers-devel krb5-devel libcap-ng-devel
BuildRequires: kernel-headers >= 2.6.29
BuildRequires: autoconf automake libtool
Requires: %{name}-libs = %{version}-%{release}
%if %{WITH_SYSTEMD}
BuildRequires: systemd
Requires(post): systemd-units systemd-sysv chkconfig coreutils
Requires(preun): systemd-units
Requires(postun): systemd-units coreutils
%else
Requires: chkconfig
%endif

%description
The audit package contains the user space utilities for
storing and searching the audit records generate by
the audit subsystem in the Linux 2.6 kernel.

%package libs
Summary: Dynamic library for libaudit
License: LGPLv2+
Group: Development/Libraries

%description libs
The audit-libs package contains the dynamic libraries needed for 
applications to use the audit framework.

%package libs-devel
Summary: Header files for libaudit
License: LGPLv2+
Group: Development/Libraries
Requires: %{name}-libs = %{version}
Requires: kernel-headers >= 2.6.29

%description libs-devel
The audit-libs-devel package contains the header files needed for
developing applications that need to use the audit framework libraries.

%package libs-static
Summary: Static version of libaudit library
License: LGPLv2+
Group: Development/Libraries
Requires: kernel-headers >= 2.6.29

%description libs-static
The audit-libs-static package contains the static libraries
needed for developing applications that need to use static audit
framework libraries

%package libs-python
Summary: Python bindings for libaudit
License: LGPLv2+
Group: Development/Libraries
Requires: %{name}-libs = %{version}-%{release}

%description libs-python
The audit-libs-python package contains the bindings so that libaudit
and libauparse can be used by python.

%package libs-python3
Summary: Python3 bindings for libaudit
License: LGPLv2+
Group: Development/Libraries
BuildRequires: python3-devel swig
Requires: %{name} = %{version}-%{release}

%description libs-python3
The audit-libs-python3 package contains the bindings so that libaudit
and libauparse can be used by python3.

%package -n audispd-plugins
Summary: Plugins for the audit event dispatcher
License: GPLv2+
Group: System Environment/Daemons
BuildRequires: openldap-devel
Requires: %{name} = %{version}-%{release}
Requires: %{name}-libs = %{version}-%{release}
Requires: openldap

%description -n audispd-plugins
The audispd-plugins package provides plugins for the real-time
interface to the audit system, audispd. These plugins can do things
like relay events to remote machines or analyze events for suspicious
behavior.

%prep
%setup -q
cp %{SOURCE1} .
%patch1 -p1

%build
%configure --sbindir=/sbin --libdir=/%{_lib} --with-python=yes \
           --with-python3=yes --with-libwrap --enable-gssapi-krb5=yes \
           --with-libcap-ng=yes --with-arm --with-aarch64 \
           --enable-zos-remote \
%ifnarch aarch64 %{power64} s390 s390x
           --with-golang \
%endif
%if %{WITH_SYSTEMD}
	--enable-systemd
%endif

make %{?_smp_mflags}

%install
mkdir -p $RPM_BUILD_ROOT/{sbin,etc/audispd/plugins.d}
%if !%{WITH_SYSTEMD}
mkdir -p $RPM_BUILD_ROOT/{etc/{sysconfig,rc.d/init.d}}
%endif
mkdir -p $RPM_BUILD_ROOT/%{_mandir}/{man5,man8}
mkdir -p $RPM_BUILD_ROOT/%{_lib}
mkdir -p $RPM_BUILD_ROOT/%{_libdir}/audit
mkdir -p $RPM_BUILD_ROOT/%{_var}/log/audit
mkdir -p $RPM_BUILD_ROOT/%{_var}/spool/audit
make DESTDIR=$RPM_BUILD_ROOT install

mkdir -p $RPM_BUILD_ROOT/%{_libdir}
# This winds up in the wrong place when libtool is involved
mv $RPM_BUILD_ROOT/%{_lib}/libaudit.a $RPM_BUILD_ROOT%{_libdir}
mv $RPM_BUILD_ROOT/%{_lib}/libauparse.a $RPM_BUILD_ROOT%{_libdir}
curdir=`pwd`
cd $RPM_BUILD_ROOT/%{_libdir}
LIBNAME=`basename \`ls $RPM_BUILD_ROOT/%{_lib}/libaudit.so.1.*.*\``
ln -s ../../%{_lib}/$LIBNAME libaudit.so
LIBNAME=`basename \`ls $RPM_BUILD_ROOT/%{_lib}/libauparse.so.0.*.*\``
ln -s ../../%{_lib}/$LIBNAME libauparse.so
cd $curdir
# Remove these items so they don't get picked up.
rm -f $RPM_BUILD_ROOT/%{_lib}/libaudit.so
rm -f $RPM_BUILD_ROOT/%{_lib}/libauparse.so
rm -f $RPM_BUILD_ROOT/%{_lib}/libaudit.la
rm -f $RPM_BUILD_ROOT/%{_lib}/libauparse.la
rm -f $RPM_BUILD_ROOT/%{_libdir}/python?.?/site-packages/_audit.a
rm -f $RPM_BUILD_ROOT/%{_libdir}/python?.?/site-packages/_audit.la
rm -f $RPM_BUILD_ROOT/%{_libdir}/python?.?/site-packages/_auparse.a
rm -f $RPM_BUILD_ROOT/%{_libdir}/python?.?/site-packages/_auparse.la
rm -f $RPM_BUILD_ROOT/%{_libdir}/python?.?/site-packages/auparse.a
rm -f $RPM_BUILD_ROOT/%{_libdir}/python?.?/site-packages/auparse.la

# Move the pkgconfig file
mv $RPM_BUILD_ROOT/%{_lib}/pkgconfig $RPM_BUILD_ROOT%{_libdir}

# On platforms with 32 & 64 bit libs, we need to coordinate the timestamp
touch -r ./audit.spec $RPM_BUILD_ROOT/etc/libaudit.conf
touch -r ./audit.spec $RPM_BUILD_ROOT/usr/share/man/man5/libaudit.conf.5.gz

%ifnarch aarch64 %{power64} s390 s390x
%check
make check
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post libs -p /sbin/ldconfig

%post
# Copy default rules into place on new installation
if [ ! -e /etc/audit/audit.rules ] ; then
	cp /etc/audit/rules.d/audit.rules /etc/audit/audit.rules
fi
%if %{WITH_SYSTEMD}
%systemd_post auditd.service
%else
/sbin/chkconfig --add auditd
%endif

%preun
%if %{WITH_SYSTEMD}
%systemd_preun auditd.service
%else
if [ $1 -eq 0 ]; then
   /sbin/service auditd stop > /dev/null 2>&1
   /sbin/chkconfig --del auditd
fi
%endif

%postun libs -p /sbin/ldconfig

%postun
if [ $1 -ge 1 ]; then
   /sbin/service auditd condrestart > /dev/null 2>&1 || :
fi

%files libs
%defattr(-,root,root,-)
%{!?_licensedir:%global license %%doc}
%license lgpl-2.1.txt
/%{_lib}/libaudit.so.1*
/%{_lib}/libauparse.*
%config(noreplace) %attr(640,root,root) /etc/libaudit.conf
%{_mandir}/man5/libaudit.conf.5.gz

%files libs-devel
%defattr(-,root,root,-)
%doc contrib/skeleton.c contrib/plugin
%{_libdir}/libaudit.so
%{_libdir}/libauparse.so
%ifnarch aarch64 %{power64} s390 s390x
%dir %{_prefix}/lib/golang/src/pkg/redhat.com/audit
%{_prefix}/lib/golang/src/pkg/redhat.com/audit/audit.go
%endif
%{_includedir}/libaudit.h
%{_includedir}/auparse.h
%{_includedir}/auparse-defs.h
%{_libdir}/pkgconfig/audit.pc
%{_libdir}/pkgconfig/auparse.pc
%{_mandir}/man3/*

%files libs-static
%defattr(-,root,root,-)
%{!?_licensedir:%global license %%doc}
%license lgpl-2.1.txt
%{_libdir}/libaudit.a
%{_libdir}/libauparse.a

%files libs-python
%defattr(-,root,root,-)
%attr(755,root,root) %{python_sitearch}/_audit.so
%attr(755,root,root) %{python_sitearch}/auparse.so
%{python_sitearch}/audit.py*

%files libs-python3
%defattr(-,root,root,-)
%attr(755,root,root) %{python3_sitearch}/*

%files
%defattr(-,root,root,-)
%doc README ChangeLog contrib/capp.rules contrib/nispom.rules contrib/lspp.rules contrib/stig.rules init.d/auditd.cron
%{!?_licensedir:%global license %%doc}
%license COPYING
%attr(644,root,root) %{_mandir}/man8/audispd.8.gz
%attr(644,root,root) %{_mandir}/man8/auditctl.8.gz
%attr(644,root,root) %{_mandir}/man8/auditd.8.gz
%attr(644,root,root) %{_mandir}/man8/aureport.8.gz
%attr(644,root,root) %{_mandir}/man8/ausearch.8.gz
%attr(644,root,root) %{_mandir}/man8/autrace.8.gz
%attr(644,root,root) %{_mandir}/man8/aulast.8.gz
%attr(644,root,root) %{_mandir}/man8/aulastlog.8.gz
%attr(644,root,root) %{_mandir}/man8/auvirt.8.gz
%attr(644,root,root) %{_mandir}/man8/augenrules.8.gz
%attr(644,root,root) %{_mandir}/man8/ausyscall.8.gz
%attr(644,root,root) %{_mandir}/man7/audit.rules.7.gz
%attr(644,root,root) %{_mandir}/man5/auditd.conf.5.gz
%attr(644,root,root) %{_mandir}/man5/audispd.conf.5.gz
%attr(644,root,root) %{_mandir}/man5/ausearch-expression.5.gz
%attr(750,root,root) /sbin/auditctl
%attr(750,root,root) /sbin/auditd
%attr(755,root,root) /sbin/ausearch
%attr(755,root,root) /sbin/aureport
%attr(750,root,root) /sbin/autrace
%attr(750,root,root) /sbin/audispd
%attr(750,root,root) /sbin/augenrules
%attr(755,root,root) %{_bindir}/aulast
%attr(755,root,root) %{_bindir}/aulastlog
%attr(755,root,root) %{_bindir}/ausyscall
%attr(755,root,root) %{_bindir}/auvirt
%if %{WITH_SYSTEMD}
%attr(640,root,root) %{_unitdir}/auditd.service
%attr(750,root,root) %dir %{_libexecdir}/initscripts/legacy-actions/auditd
%attr(750,root,root) %{_libexecdir}/initscripts/legacy-actions/auditd/resume
%attr(750,root,root) %{_libexecdir}/initscripts/legacy-actions/auditd/rotate
%attr(750,root,root) %{_libexecdir}/initscripts/legacy-actions/auditd/stop
%attr(750,root,root) %{_libexecdir}/initscripts/legacy-actions/auditd/restart
%attr(750,root,root) %{_libexecdir}/initscripts/legacy-actions/auditd/condrestart
%else
%attr(755,root,root) /etc/rc.d/init.d/auditd
%config(noreplace) %attr(640,root,root) /etc/sysconfig/auditd
%endif
%attr(750,root,root) %dir %{_var}/log/audit
%attr(750,root,root) %dir /etc/audit
%attr(750,root,root) %dir /etc/audit/rules.d
%attr(750,root,root) %dir /etc/audisp
%attr(750,root,root) %dir /etc/audisp/plugins.d
%config(noreplace) %attr(640,root,root) /etc/audit/auditd.conf
%config(noreplace) %attr(640,root,root) /etc/audit/rules.d/audit.rules
%ghost %config(noreplace) %attr(640,root,root) /etc/audit/audit.rules
%config(noreplace) %attr(640,root,root) /etc/audisp/audispd.conf
%config(noreplace) %attr(640,root,root) /etc/audisp/plugins.d/af_unix.conf
%config(noreplace) %attr(640,root,root) /etc/audisp/plugins.d/syslog.conf

%files -n audispd-plugins
%defattr(-,root,root,-)
%attr(644,root,root) %{_mandir}/man8/audispd-zos-remote.8.gz
%attr(644,root,root) %{_mandir}/man5/zos-remote.conf.5.gz
%config(noreplace) %attr(640,root,root) /etc/audisp/plugins.d/audispd-zos-remote.conf
%config(noreplace) %attr(640,root,root) /etc/audisp/zos-remote.conf
%attr(750,root,root) /sbin/audispd-zos-remote
%config(noreplace) %attr(640,root,root) /etc/audisp/audisp-remote.conf
%config(noreplace) %attr(640,root,root) /etc/audisp/plugins.d/au-remote.conf
%attr(750,root,root) /sbin/audisp-remote
%attr(700,root,root) %dir %{_var}/spool/audit
%attr(644,root,root) %{_mandir}/man5/audisp-remote.conf.5.gz
%attr(644,root,root) %{_mandir}/man8/audisp-remote.8.gz

%changelog
* Thu Jul 16 2015 Steve Grubb <sgrubb@redhat.com> 2.4.3-1
- New upstream bugfix release
- Adds python3 support

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Tue Apr 28 2015 Steve Grubb <sgrubb@redhat.com> 2.4.2-1
- New upstream bugfix release

* Sat Feb 21 2015 Till Maas <opensource@till.name> - 2.4.1-2
- Rebuilt for Fedora 23 Change
  https://fedoraproject.org/wiki/Changes/Harden_all_packages_with_position-independent_code

* Tue Oct 28 2014 Steve Grubb <sgrubb@redhat.com> 2.4.1-1
- New upstream feature and bugfix release

* Mon Oct 06 2014 Karsten Hopp <karsten@redhat.com> 2.4-2
- bump release and rebuild for upgradepath

* Sun Aug 24 2014 Steve Grubb <sgrubb@redhat.com> 2.4-1
- New upstream feature and bugfix release

* Fri Aug 15 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.3.8-0.3.svn20140803
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Mon Aug  4 2014 Peter Robinson <pbrobinson@fedoraproject.org> 2.3.8-0.2.svn20140803
- aarch64/PPC/s390 don't have golang

* Sat Aug 02 2014 Steve Grubb <sgrubb@redhat.com> 2.3.8-0.1.svn20140803
- New upstream svn snapshot

* Tue Jul 22 2014 Steve Grubb <sgrubb@redhat.com> 2.3.7-4
- Bug 1117953 - Per fesco#1311, please disable syscall auditing by default

* Fri Jul 11 2014 Tom Callaway <spot@fedoraproject.org> - 2.3.7-3
- mark license files properly

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.3.7-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue Jun 03 2014 Steve Grubb <sgrubb@redhat.com> 2.3.7-1
- New upstream bugfix release

* Fri Apr 11 2014 Steve Grubb <sgrubb@redhat.com> 2.3.6-1
- New upstream bugfix/enhancement release

* Mon Mar 17 2014 Steve Grubb <sgrubb@redhat.com> 2.3.5-1
- New upstream bugfix/enhancement release

* Thu Feb 27 2014 Steve Grubb <sgrubb@redhat.com> 2.3.4-1
- New upstream bugfix/enhancement release

* Thu Jan 16 2014 Steve Grubb <sgrubb@redhat.com> 2.3.3-1
- New upstream bugfix/enhancement release

* Mon Jul 29 2013 Steve Grubb <sgrubb@redhat.com> 2.3.2-1
- New upstream bugfix/enhancement release

* Fri Jun 21 2013 Steve Grubb <sgrubb@redhat.com> 2.3.1-3
- Drop prelude support

* Fri May 31 2013 Steve Grubb <sgrubb@redhat.com> 2.3.1-2
- Fix unknown lvalue in auditd.service (#969345)

* Thu May 30 2013 Steve Grubb <sgrubb@redhat.com> 2.3.1-1
- New upstream bugfix/enhancement release

* Fri May 03 2013 Steve Grubb <sgrubb@redhat.com> 2.3-2
- If no rules exist, copy shipped rules into place

* Tue Apr 30 2013 Steve Grubb <sgrubb@redhat.com> 2.3-1
- New upstream bugfix release

* Thu Mar 21 2013 Steve Grubb <sgrubb@redhat.com> 2.2.3-2
- Fix clone syscall interpretation

* Tue Mar 19 2013 Steve Grubb <sgrubb@redhat.com> 2.2.3-1
- New upstream bugfix release

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.2.2-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Jan 16 2013 Steve Grubb <sgrubb@redhat.com> 2.2.2-4
- Don't make auditd.service file executable (#896113)

* Fri Jan 11 2013 Steve Grubb <sgrubb@redhat.com> 2.2.2-3
- Do not own /usr/lib64/audit

* Wed Dec 12 2012 Steve Grubb <sgrubb@redhat.com> 2.2.2-2
- New upstream release

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.2.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Mar 23 2012 Steve Grubb <sgrubb@redhat.com> 2.2.1-1
- New upstream release

* Thu Mar 1 2012 Steve Grubb <sgrubb@redhat.com> 2.2-1
- New upstream release

* Thu Jan 12 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.1.3-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Thu Sep 15 2011 Adam Williamson <awilliam@redhat.com> 2.1.3-4
- add in some systemd scriptlets that were missed, including one which
  will cause auditd to be enabled on upgrade from pre-systemd builds

* Wed Sep 14 2011 Steve Grubb <sgrubb@redhat.com> 2.1.3-3
- Enable by default (#737060)

* Tue Aug 30 2011 Steve Grubb <sgrubb@redhat.com> 2.1.3-2
- Correct misplaced %ifnarch (#734359)

* Mon Aug 15 2011 Steve Grubb <sgrubb@redhat.com> 2.1.3-1
- New upstream release

* Tue Jul 26 2011 Jóhann B. Guðmundsson <johannbg@gmail.com> - 2.1.2-2
- Introduce systemd unit file, drop SysV support

* Sat Jun 11 2011 Steve Grubb <sgrubb@redhat.com> 2.1.2-1
- New upstream release

* Wed Apr 20 2011 Steve Grubb <sgrubb@redhat.com> 2.1.1-1
- New upstream release

* Tue Mar 29 2011 Steve Grubb <sgrubb@redhat.com> 2.1-1
- New upstream release

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Feb 04 2011 Steve Grubb <sgrubb@redhat.com> 2.0.6-1
- New upstream release

* Thu Jan 20 2011 Karsten Hopp <karsten@redhat.com> 2.0.5-2
- bump and rebuild as 2.0.5-1 was erroneously linked with python-2.6 on ppc

* Tue Nov 02 2010 Steve Grubb <sgrubb@redhat.com> 2.0.5-1
- New upstream release

* Wed Jul 21 2010 David Malcolm <dmalcolm@redhat.com> - 2.0.4-4
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Tue Feb 16 2010 Adam Jackson <ajax@redhat.com> 2.0.4-3
- audit-2.0.4-add-needed.patch: Fix FTBFS for --no-add-needed

* Fri Jan 29 2010 Steve Grubb <sgrubb@redhat.com> 2.0.4-2
- Split out static libs (#556039)

* Tue Dec 08 2009 Steve Grubb <sgrubb@redhat.com> 2.0.4-1
- New upstream release

* Sat Oct 17 2009 Steve Grubb <sgrubb@redhat.com> 2.0.3-1
- New upstream release

* Fri Oct 16 2009 Steve Grubb <sgrubb@redhat.com> 2.0.2-1
- New upstream release

* Mon Sep 28 2009 Steve Grubb <sgrubb@redhat.com> 2.0.1-1
- New upstream release

* Fri Aug 21 2009 Steve Grubb <sgrubb@redhat.com> 2.0-3
- New upstream release
