# TODO
# - missing archivedir in logrotate (or intentionally?)
# - make it use /var/lib/murmur

%define		qtver	4.6.2
%define		snap	20100401

Summary:	Voice chat software primarily intended for use while gaming
Name:		mumble
Version:	1.2.2
Release:	0.6
License:	BSD and Custom (see LICENSE)
Group:		Applications/Communications
Source0:	http://downloads.sourceforge.net/mumble/%{name}-%{version}.tar.gz
# Source0-md5:	de30ee85170e183b66568b53b04c5727
# get it via: git clone git://mumble.git.sourceforge.net/gitroot/mumble/mumble
#Source0:	%{name}-%{version}-%{snap}.tar.gz
URL:		http://mumble.sourceforge.net/
Source1:	murmur.init
Source2:	%{name}.desktop
Source3:	%{name}-overlay.desktop
Source4:	murmur.logrotate
Patch0:		%{name}-compile-fix.patch
Patch1:		%{name}-murmurini.patch
BuildRequires:	QtCore-devel >= %{qtver}
BuildRequires:	QtDBus-devel >= %{qtver}
BuildRequires:	QtGui-devel >= %{qtver}
BuildRequires:	QtNetwork-devel >= %{qtver}
BuildRequires:	QtOpenGL-devel >= %{qtver}
BuildRequires:	QtSql-devel >= %{qtver}
BuildRequires:	QtSvg-devel >= %{qtver}
BuildRequires:	QtXml-devel >= %{qtver}
BuildRequires:	QtXmlPatterns-devel >= %{qtver}
BuildRequires:	celt-devel >= 0.7.1
BuildRequires:	ice-devel
BuildRequires:	protobuf
BuildRequires:	qt4-build >= %{qtver}
BuildRequires:	qt4-qmake >= %{qtver}
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	speech-dispatcher-devel
BuildRequires:	speex-devel
Requires:	QtSql-sqlite3 >= %{qtver}
Requires:	speech-dispatcher
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_appdir		/var/lib/murmur

%description
Low-latency, high-quality voice communication for gamers. Includes
game linking, so voice from other players comes from the direction of
their characters, and has echo cancellation so the sound from your
loudspeakers won't be audible to other players.

%package server
Summary:	Mumble voice chat server
Group:		Applications/Communications
Requires(post,preun):	/sbin/chkconfig
Requires:	QtSql-sqlite3 >= %{qtver}
Requires:	rc-scripts >= 0.4.1.23

%description server
Murmur (also called mumble-server) is part of VoIP suite Mumble
primarily intended for gamers. Murmur is server part of suite.

%prep
%setup -q
%patch0 -p1
%patch1 -p0

%build
qmake-qt4 "CONFIG+=no-bundled-speex no-bundled-celt no-g15 \
no-embed-qt-translations no-update \
QMAKE_CFLAGS=%{rpmcflags} \
QMAKE_CXXFLAGS=%{rpmcxxflags} \
QMAKE_CFLAGS_RELEASE=%{rpmcflags} \
QMAKE_CXXFLAGS_RELEASE=%{rpmcxxflags} \
DEFINES+=PLUGIN_PATH=%{_libdir}/%{name} \
DEFINES+=DEFAULT_SOUNDSYSTEM=PulseAudio" main.pro
%{__make} -j1

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT{%{_sbindir},%{_bindir},%{_libdir}/%{name},%{_sysconfdir}/murmur,%{_desktopdir}}
install -d $RPM_BUILD_ROOT{%{_iconsdir}/hicolor/{16x16,32x32,48x48,64x64},%{_pixmapsdir}}
install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,%{_appdir}}
install -d $RPM_BUILD_ROOT/etc/logrotate.d

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install -p %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/murmurd
install -p %{SOURCE2} $RPM_BUILD_ROOT%{_desktopdir}
cp -a %{SOURCE4} $RPM_BUILD_ROOT/etc/logrotate.d/murmur
install -p release/libmumble.so.*.*.* $RPM_BUILD_ROOT%{_libdir}
install -p release/mumble* $RPM_BUILD_ROOT%{_bindir}
install -p release/murmurd $RPM_BUILD_ROOT%{_sbindir}
install -p release/plugins/*.so $RPM_BUILD_ROOT%{_libdir}/%{name}
cp -a scripts/murmur.ini $RPM_BUILD_ROOT%{_sysconfdir}/murmur
#cp -a src/mumble11x/resources/mumble.16x16.png $RPM_BUILD_ROOT%{_iconsdir}/hicolor/16x16/%{name}.png
cp -a src/mumble11x/resources/mumble.32x32.png $RPM_BUILD_ROOT%{_pixmapsdir}/%{name}.png
#cp -a src/mumble11x/resources/mumble.48x48.png $RPM_BUILD_ROOT%{_iconsdir}/hicolor/48x48/%{name}.png
#cp -a src/mumble11x/resources/mumble.64x64.png $RPM_BUILD_ROOT%{_iconsdir}/hicolor/64x64/%{name}.png

%clean
rm -rf $RPM_BUILD_ROOT

%post   -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%pre server
%groupadd -g 250 murmur
%useradd -u 250 -d /var/lib/murmur -g murmur -c "Mumble Server" murmur

%post server
if [ ! -f /var/log/murmur ]; then
	umask 027
	touch /var/log/murmur
fi
/sbin/chkconfig --add murmurd
%service murmurd restart "mumble server"

%preun server
if [ "$1" = "0" ]; then
	%service murmurd stop
	/sbin/chkconfig --del murmurd
fi

%files
%defattr(644,root,root,755)
%doc README README.Linux LICENSE CHANGES
%attr(755,root,root) %{_bindir}/mumble
%attr(755,root,root) %{_bindir}/mumble11x
%attr(755,root,root) %{_libdir}/libmumble.so.*.*.*
%dir %{_libdir}/%{name}
%attr(755,root,root) %{_libdir}/%{name}/*.so
%{_desktopdir}/%{name}.desktop
%{_pixmapsdir}/%{name}.png

%files server
%defattr(644,root,root,755)
%attr(750,root,root) %dir %{_sysconfdir}/murmur
%attr(770,root,murmur) %dir %{_appdir}
%attr(640,root,murmur) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/murmur/murmur.ini
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/murmur
%attr(755,root,root) %{_sbindir}/murmurd
%attr(754,root,root) /etc/rc.d/init.d/murmurd
