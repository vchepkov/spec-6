Name:           monit
Version:        5.8.1
Release:        1%{?dist}
Summary:        Manages and monitors processes, files, directories and devices

Group:          Applications/Internet
License:        GPLv3+
URL:            http://www.tildeslash.com/monit
Source0:        http://www.tildeslash.com/monit/dist/monit-%{version}.tar.gz
Source1:        monit.init
Source2:        monit.logrotate
Source3:        monit.pam
Patch1:         monit-no-startup-msg.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  flex
BuildRequires:  openssl-devel
BuildRequires:  pam-devel
BuildRequires:  byacc
BuildRequires:  bash
BuildRequires:  /usr/bin/pod2man

Requires(post): /sbin/chkconfig
Requires(preun): /sbin/chkconfig
Requires(preun): /sbin/service
Requires(postun): /sbin/service

%description
monit is a utility for managing and monitoring, processes, files, directories
and devices on a UNIX system. Monit conducts automatic maintenance and repair
and can execute meaningful causal actions in error situations.

%prep
%setup -q
%patch1 -p1 -b .nomsg

%build
%configure --disable-static
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

install -p -D -m0755 %{SOURCE1} $RPM_BUILD_ROOT%{_initrddir}/monit
install -p -D -m0755 monit $RPM_BUILD_ROOT%{_bindir}/monit

mkdir -p $RPM_BUILD_ROOT%{_sharedstatedir}/monit
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/spool/monit

mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/rpm-state

# Log file & logrotate config
install -p -D -m0644 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/monit
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/log
install -m0600 /dev/null $RPM_BUILD_ROOT%{_localstatedir}/log/monit

# PAM file

install -p -D -m0644 %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/monit

# Let's include some good defaults
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/monit.d
echo "
# Set daemon mode timeout to 1 minute
set daemon 60

## Set the location of the Monit id file which stores the unique id for the
## Monit instance. The id is generated and stored on first Monit start. By
## default the file is placed in $HOME/.monit.id.

set idfile %{_sharedstatedir}/monit/monit.id

## Set the location of the Monit state file which saves monitoring states
## on each cycle. By default the file is placed in $HOME/.monit.state. If
## the state file is stored on a persistent filesystem, Monit will recover
## the monitoring state across reboots. If it is on temporary filesystem, the
## state will be lost on reboot which may be convenient in some situations.

set statefile %{_sharedstatedir}/monit/monit.state

## By default Monit will drop alert events if no mail servers are available.
## If you want to keep the alerts for later delivery retry, you can use the
## EVENTQUEUE statement. The base directory where undelivered alerts will be
## stored is specified by the BASEDIR option. You can limit the maximal queue
## size using the SLOTS option (if omitted, the queue is limited by space
## available in the back end filesystem).

set eventqueue
    basedir %{_localstatedir}/spool/monit
    slots 100

## Set the list of mail servers for alert delivery. Multiple servers may be
## specified using a comma separator. If the first mail server fails, Monit
## will use the second mail server in the list and so on. By default Monit uses
## port 25 - it is possible to override this with the PORT option.

set mailserver localhost

# Include all files from %{_sysconfdir}/monit.d/
include %{_sysconfdir}/monit.d/*" > $RPM_BUILD_ROOT%{_sysconfdir}/monitrc

echo "# log to monit.log
set logfile /var/log/monit
" > $RPM_BUILD_ROOT%{_sysconfdir}/monit.d/logging

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add monit

%preun
if [ $1 = 0 ]; then
        /sbin/service monit stop >/dev/null 2>&1
        /sbin/chkconfig --del monit
fi

%postun
if [ "$1" -ge "1" ]; then
        /sbin/service monit condrestart >/dev/null 2>&1 || :
fi

%triggerun -- monit < 5.8.1-1
/bin/ps -eo comm|grep -qw monit && touch %{_localstatedir}/lib/rpm-state/monit.running >/dev/null 2>&1 || :
/sbin/stop monit >/dev/null 2>&1 || :

%triggerpostun  -- monit < 5.8.1-1
[ -e %{_localstatedir}/lib/rpm-state/monit.running ] && /sbin/service monit start >/dev/null 2>&1 || :
rm -f %{_localstatedir}/lib/rpm-state/monit.running

%files
%defattr(-,root,root,-)
%doc COPYING README
%attr(600,-,-) %config(noreplace) %{_sysconfdir}/monitrc
%config(noreplace) %{_sysconfdir}/monit.d/logging
%config(noreplace) %{_sysconfdir}/logrotate.d/monit
%config(noreplace) %{_sysconfdir}/pam.d/monit
%ghost %{_localstatedir}/log/monit
%{_sysconfdir}/monit.d/
%{_initrddir}/monit
%{_bindir}/monit
%{_mandir}/man1/monit.1*
%{_sharedstatedir}/monit
%{_localstatedir}/spool/monit
%{_localstatedir}/lib/rpm-state

%changelog
* Thu May 15 2014 Vadym Chepkov <vchepkov@gmail.com> - 5.8.1-1
- update to 5.8.1
- switched from upstart to init due to incompatibility

* Thu May 01 2014 Vadym Chepkov <vchepkov@gmail.com> - 5.8-2
- added workaround for upstart bug, preventing process to stop

* Fri Mar 28 2014 Vadym Chepkov <vchepkov@gmail.com> - 5.8-1
- update to 5.8

* Tue Mar 25 2014 Vadym Chepkov <vchepkov@gmail.com> - 5.7-1
- update to 5.7

* Thu Jan 02 2014 Vadym Chepkov <vchepkov@gmail.com> - 5.6-3
- changed to upstart
- secured default configuration
- added PAM configuration


* Thu Dec 12 2013 Vadym Chepkov <vchepkov@gmail.com> - 5.6-2
- corrected config file name

* Thu Nov 21 2013 Vadym Chepkov <vchepkov@bna.com> - 5.6-1
- upgrade to 5.6

* Sat Jul 14 2012 Maxim Burgerhout <wzzrd@fedoraproject.org> - 5.1.1-4
- Fix init script to contain the name of the pidfile

* Wed Jul 11 2012 Maxim Burgerhout <wzzrd@fedoraproject.org> - 5.1.1-3
- Fix init script to use the pidfile instead of the process name to kill the
  daemon

* Thu Aug 05 2010 Maxim Burgerhout <wzzrd@fedoraproject.org> - 5.1.1-2
- Enabled PAM authentication (bz #621599)

* Mon Jul 05 2010 Maxim Burgerhout <wzzrd@fedoraproject.org> - 5.1.1-1
- Version bump to 5.1.1 (needed new version of monit-no-startup-msg.patch)
- Ghosted the logfile

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> - 5.0.3-2
- rebuilt with new openssl

* Fri Aug 14 2009 Stewart Adam <s.adam at diffingo.com> - 5.0.3-1
- Update to 5.0.3 (thanks to Lubomir Rintel of Good Data for the patch)

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.10.1-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.10.1-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Jan 17 2009 Tomas Mraz <tmraz@redhat.com> 4.10.1-9
- rebuild with new openssl

* Mon Dec 22 2008 Stewart Adam <s.adam at diffingo.com> 4.10.1-8
- Tweak configuration defaults: include /etc/monit.d/*, log to /var/log/monit
  and set daemon time to 60s
- Don't use $desc in initscript
- Add patch to search for monit.conf by default (#475044)
- Add patch to remove redundant startup message

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 4.10.1-7
- Autorebuild for GCC 4.3

* Wed Dec 05 2007 Release Engineering <rel-eng at fedoraproject dot org> - 4.10.1-6
 - Rebuild for deps

* Wed Dec 5 2007 Stewart Adam <s.adam at diffingo.com> 4.10.1-5
- Rebuild to fix broken deps on libssl.so.6 and libcrypto.so.6

* Sat Nov 24 2007 Stewart Adam <s.adam at diffingo.com> 4.10.1-4
- Substitute RPM macros for their real values in monit.conf (#397671)

* Tue Nov 13 2007 Stewart Adam <s.adam at diffingo.com> 4.10.1-3
- Bump
- Fix changelog date for previous entry

* Mon Nov 12 2007 Stewart Adam <s.adam at diffingo.com> 4.10.1-2.1
- Switch back to OpenSSL since NSS isn't working too well with Monit

* Wed Nov 7 2007 Stewart Adam <s.adam at diffingo.com> 4.10.1-2
- License is actually GPLv3+
- s/%%{__install}/%%{__install} -p/
- NSS-ize

* Tue Nov 6 2007 Stewart Adam <s.adam at diffingo.com> 4.10.1-1
- Initial RPM release
