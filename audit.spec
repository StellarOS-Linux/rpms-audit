Summary: User space tools for 2.6 kernel auditing.
Name: audit
Version: 0.7.2
Release: 2
License: GPL
Group: System Environment/Daemons
URL: http://people.redhat.com/sgrubb/audit/
Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildRequires: libtool
BuildRequires: glibc-kernheaders >= 2.4-9.1.90
BuildRequires: automake >= 1.9
BuildRequires: autoconf >= 2.59
Requires: %{name}-libs = %{version}-%{release}
Requires: chkconfig

%description
The audit package contains the user space utilities for
storing and processing the audit records generate by
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
Requires: glibc-kernheaders >= 2.4-9.1.90

%description libs-devel
The audit-libs-devel package contains the static libraries and header 
files needed for developing applications that need to use the audit 
framework libraries.

%prep
%setup -q

%build
autoreconf -fv --install
export CFLAGS="$RPM_OPT_FLAGS"
./configure --sbindir=/sbin --mandir=%{_mandir} --libdir=/%{_lib}
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
ln -s ../../%{_lib}/libaudit.so libaudit.so
cd $curdir

%clean
rm -rf $RPM_BUILD_ROOT

%post libs -p /sbin/ldconfig

%post
if [ $1 = 1 ]; then
   /sbin/chkconfig --add auditd
fi

%preun
if [ $1 = 0 ]; then
   /sbin/service auditd stop > /dev/null 2>&1
   /sbin/chkconfig --del auditd
fi

%postun libs
/sbin/ldconfig 2>/dev/null

%postun
if [ $1 -ge 1 ]; then
   /sbin/service auditd condrestart > /dev/null 2>&1
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

%files
%defattr(-,root,root,-)
%doc README COPYING ChangeLog sample.rules
%attr(0644,root,root) %{_mandir}/man8/*
%attr(750,root,root)  /sbin/auditctl
%attr(750,root,root)  /sbin/auditd
%attr(750,root,root) /sbin/ausearch
%attr(750,root,root) /sbin/autrace
%attr(755,root,root) /etc/rc.d/init.d/auditd
%attr(750,root,root) %{_var}/log/audit
%config(noreplace) %attr(640,root,root) /etc/auditd.conf
%config(noreplace) %attr(640,root,root) /etc/audit.rules
%config(noreplace) %attr(640,root,root) /etc/sysconfig/auditd


%changelog
* Wed Apr 27 2005 Steve Grubb <sgrubb@redhat.com> 0.7.2-1
- Allow ausearch uid & gid to be non-numeric (root, wheel, etc)
- Fix problems with changing run level
- Added new code for logging shutdown reason credentials
- Update DAEMON messages to use better timestamp

* Sun Apr 24 2005 Steve Grubb <sgrubb@redhat.com> 0.7.1-1
- Make sure time calc is done using localtime
- Raise rlimits for file size & cpu usage
- Added new disk_error_action config item to auditd.conf
- Rework memory management of event buffer
- Handled all errors in event logging thread

* Sat Apr 23 2005 Steve Grubb <sgrubb@redhat.com> 0.7-1
- In auditctl -l, loop until all rules are printed
- Update autrace not to run if rules are currently loaded
- Added code to switch to single user mode when disk is full
- Added the ausearch program

* Wed Apr 20 2005 Steve Grubb <sgrubb@redhat.com> 0.6.12-1
- Fixed bug where elf type wasn't being set when given numerically
- Added autrace program (similar to strace)
- Fixed bug when logs = 2 and ROTATE is the action, only 1 log resulted

* Mon Apr 18 2005 Steve Grubb <sgrubb@redhat.com> 0.6.11-1
- Check log file size on start up
- Added priority_boost config item
- Reworked arch support
- Reworked how run level is changed
- Make allowances for ECONNREFUSED

* Fri Apr  1 2005 Steve Grubb <sgrubb@redhat.com> 0.6.10-1
- Code cleanups
- Support the arch field for auditctl
- Add version to auditctl
- Documentation updates
- Moved default location of the audit log to /var/log/audit

* Thu Mar 17 2005 Steve Grubb <sgrubb@redhat.com> 0.6.9-1
- Added patch for filesystem watch
- Added version information to audit start message
- Change netlink code to use ack in order to get error notification

* Wed Mar 10 2005 Steve Grubb <sgrubb@redhat.com> 0.6.8-1
- removed the pam_loginuid library - its going to pam

* Wed Mar 9 2005 Steve Grubb <sgrubb@redhat.com> 0.6.7-1
- Fixed bug setting loginuid
- Added num_logs to configure number of logs when rotating
- Added code for rotating logs

* Tue Mar 8 2005 Steve Grubb <sgrubb@redhat.com> 0.6.6-1
- Fix audit_set_pid to try to read a reply, but its non-fatal if no reply.
- Remove the read status during init
- Change to using pthreads sync mechanism for stopping system
- Worker thread should ignore all signals
- Change main loop to use select for inbound event handling
- Gave pam_loginuid a "failok" option for testing

* Thu Mar 3 2005 Steve Grubb <sgrubb@redhat.com> 0.6.5-1
- Lots of code cleanups
- Added write_pid function to auditd
- Added audit_log to libaudit
- Don't check file length in foreground mode of auditd
- Added *if_enabled functions to send messages only if audit system is enabled
- If syscall name is unknown when printing rules, use the syscall number
- Rework the build system to produce singly threaded public libraries
- Create a multithreaded version of libaudit for the audit daemon's use

* Wed Feb 23 2005 Steve Grubb <sgrubb@redhat.com> 0.6.4-1
- Rename pam_audit to pam_loginuid to reflect what it does
- Fix bug in detecting space left on partition
- Fix bug in handling of suspended logging

* Wed Feb 23 2005 David Woodhouse <dwmw2@redhat.com> 0.6.3-3
- Include stdint.h in libaudit.h and require new glibc-kernheaders

* Sun Feb 20 2005 Steve Grubb <sgrubb@redhat.com> 0.6.3-2
- Another lib64 correction

* Sun Feb 20 2005 Steve Grubb <sgrubb@redhat.com> 0.6.3-1
- Change pam install from /lib/security to /%{_lib}/security
- Change pam_audit to write loginuid to /proc/pid/loginuid
- Add pam_session_close handle
- Update to newest kernel headers

* Fri Feb 11 2005 Steve Grubb <sgrubb@redhat.com> 0.6.2-1
- New version
- Add R option to auditctl to allow reading rules from file.
- Do not allow task creation list to have syscall auditing
- Add D option to allow deleting all rules with 1 command
- Added pam_audit man page & sample.rules
- Mod initscript to call auditctl to load rules at start-up
- Write message to log file for daemon start up
- Write message that daemon is shutting down
- Modify auditd shutdown to wait until logger thread is finished
- Add sample rule file to docs

* Sat Jan 08 2005 Steve Grubb <sgrubb@redhat.com> 0.6.1-1
- New version: rework auditctl and its man pages.
- Added admin_space_left config option as last chance before
  running out of disk space.

* Wed Jan 05 2005 Steve Grubb <sgrubb@redhat.com> 0.6-1
- New version
- Split package up to libs, libs-devel, and audit.

* Mon Dec 13 2004 Steve Grubb <sgrubb@redhat.com> 0.5.6-1
- New version

* Fri Dec 10 2004 Steve Grubb <sgrubb@redhat.com> 0.5.5-1
- New version

* Fri Dec 03 2004 Steve Grubb <sgrubb@redhat.com> 0.5.4-1
- New version

* Mon Nov 22 2004 Steve Grubb <sgrubb@redhat.com> 0.5.3-1
- New version

* Mon Nov 15 2004 Steve Grubb <sgrubb@redhat.com> 0.5.2-1
- New version

* Wed Nov 10 2004 Steve Grubb <sgrubb@redhat.com> 0.5.1-1
- Added initscript pieces
- New version

* Wed Sep  1 2004 Charlie Bennett (ccb@redhat.com) 0.5-1 
- Initial build.

