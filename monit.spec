Name:           monit
Version:        5.6
Release:        2%{?dist}
Summary:        Manages and monitors processes, files, directories and devices

Group:          Applications/Internet
License:        GPLv3+
URL:            http://www.tildeslash.com/monit
Source0:        http://www.tildeslash.com/monit/dist/monit-%{version}.tar.gz
Source1:        monit-sysv-initscript
Source2:        monit.logrotate
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  flex
BuildRequires:  openssl-devel
BuildRequires:  pam-devel
BuildRequires:  byacc
BuildRequires:  bash

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

%build
%configure --disable-static
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

install -p -D -m0755 %{SOURCE1} $RPM_BUILD_ROOT%{_initrddir}/monit
install -p -D -m0600 monitrc $RPM_BUILD_ROOT%{_sysconfdir}/monitrc
install -p -D -m0755 monit $RPM_BUILD_ROOT%{_bindir}/monit

# Log file & logrotate config
install -p -D -m0644 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/monit
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/log
install -m0600 /dev/null $RPM_BUILD_ROOT%{_localstatedir}/log/monit

# Let's include some good defaults
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/monit.d
echo "
# set daemon mode timeout to 1 minute
set daemon 60
# Include all files from %{_sysconfdir}/monit.d/
include %{_sysconfdir}/monit.d/*" >> $RPM_BUILD_ROOT%{_sysconfdir}/monitrc

echo "# log to monit.log
set logfile /var/log/monit
" > $RPM_BUILD_ROOT%{_sysconfdir}/monit.d/logging


%clean
rm -rf $RPM_BUILD_ROOT

%post
# This adds the proper /etc/rc*.d links for the script
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


%files
%defattr(-,root,root,-)
%doc CHANGES COPYING README 
%config(noreplace) %{_sysconfdir}/monitrc
%config(noreplace) %{_sysconfdir}/monit.d/logging
%config(noreplace) %{_sysconfdir}/logrotate.d/monit
%ghost %{_localstatedir}/log/monit
%{_sysconfdir}/monit.d/
%{_initrddir}/monit
%{_bindir}/%{name}
%{_mandir}/man1/monit.1*

%changelog
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
