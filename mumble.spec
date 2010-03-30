Summary:	Voice chat software primarily intended for use while gaming
Name:		mumble
Version:	1.2.2
Release:	1
License:	BSD
Group:		Applications/Networking
Source0:	http://dl.sourceforge.net/mumble/%{name}-%{version}.tar.gz
# Source0-md5:	de30ee85170e183b66568b53b04c5727
URL:		http://mumble.sourceforge.net/
Source1:	murmur.init
Source2:	%{name}.desktop
Source3:	%{name}-overlay.desktop
#fixes compile error on f10 and above
Patch0:		%{name}-compile-fix.patch
BuildRequires:	alsa-lib-devel
BuildRequires:	alsa-oss-devel
BuildRequires:	boost-devel
BuildRequires:	dbus-qt-devel
BuildRequires:	desktop-file-utils
BuildRequires:	ice-devel
BuildRequires:	libcap-devel
BuildRequires:	libogg-devel
BuildRequires:	openssl-devel
BuildRequires:	pulseaudio-libs-devel
BuildRequires:	qt-devel
BuildRequires:	speech-dispatcher-devel
BuildRequires:	speex-devel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Low-latency, high-quality voice communication for gamers. Includes
game linking, so voice from other players comes from the direction of
their characters, and has echo cancellation so the sound from your
loudspeakers won't be audible to other players.

%package -n murmur
Summary:	Mumble voice chat server
Group:		Daemons
Provides:	%{name}-server = %{version}-%{release}

Requires(post):	chkconfig
Requires(postun):	initscripts
Requires(pre):	shadow-utils
Requires(preun):	chkconfig, initscripts

%description -n murmur
Murmur(also called mumble-server) is part of VoIP suite Mumble
primarily intended for gamers. Murmur is server part of suite.

%package plugins
Summary:	Plugins for VoIP program Mumble
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description plugins
Mumble-plugins is part of VoIP suite Mumble primarily intended for
gamers. This plugin allows game linking so the voice of players will
come from the direction of their characters.

%package overlay
Summary:	Start Mumble with overlay
Group:		Applications/Networking
Requires:	%{name} = %{version}-%{release}

%description overlay
Mumble-overlay is part of VoIP suite Mumble primarily intended for
gamers. Mumble-overlay shows players in current channel and linked
channels in game so you don't need to quit the game to see who is in
your channel.

%package protocol
Summary:	Package to support mumble protocol
Group:		Applications/Networking
Requires:	%{name} = %{version}-%{release}

%description protocol
Low-latency, high-quality voice communication for gamers. Includes
game linking, so voice from other players comes from the direction of
their characters, and has echo cancellation so the sound from your
loudspeakers won't be audible to other players.

%pre -n murmur
getent group mumble-server >/dev/null || groupadd -r mumble-server
getent passwd mumble-server >/dev/null || \
useradd -r -g mumble-server -d %{_localstatedir}/lib/%{name}-server/ -s /sbin/nologin \
-c "Mumble-server(murmur) user" mumble-server
exit 0

%prep
%setup -q
%patch0 -p1

%build
qmake-qt4 "CONFIG+=no-bundled-speex no-g15 \
no-embed-qt-translations no-update \
QMAKE_CFLAGS_RELEASE=%{optflags} \
QMAKE_CXXFLAGS_RELEASE=%{optflags} \
DEFINES+=PLUGIN_PATH=%{_libdir}/%{name} \
DEFINES+=DEFAULT_SOUNDSYSTEM=PulseAudio" main.pro
%{__make} %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT

install -pD release/%{name} $RPM_BUILD_ROOT%{_bindir}/%{name}
install -pD release/murmurd $RPM_BUILD_ROOT%{_sbindir}/murmurd
ln -s murmurd $RPM_BUILD_ROOT%{_sbindir}/%{name}-server
#ln -s ../sbin/murmurd $RPM_BUILD_ROOT%{_sbindir}/murmur

install -d $RPM_BUILD_ROOT%{_libdir}/%{name}/
#install -d $RPM_BUILD_ROOT%{_libdir}/%{name}/
#install -p release/libmumble.so* $RPM_BUILD_ROOT%{_libdir}/
# obviusly install doesn't preserve symlinks
# mumble will complain loudly if it cant find libmumble.so inside %{_libdir}/
install -p release/libmumble.so.%{version} $RPM_BUILD_ROOT%{_libdir}/
ln -s %{_libdir}/libmumble.so.%{version} $RPM_BUILD_ROOT%{_libdir}/libmumble.so
ln -s %{_libdir}/libmumble.so.%{version} $RPM_BUILD_ROOT%{_libdir}/libmumble.so.1
ln -s %{_libdir}/libmumble.so.%{version} $RPM_BUILD_ROOT%{_libdir}/libmumble.so.1.1
install -p release/plugins/*.so $RPM_BUILD_ROOT%{_libdir}/%{name}/
ln -s %{_libdir}/libmumble.so.%{version} $RPM_BUILD_ROOT%{_libdir}/%{name}/libmumble.so
ln -s %{_libdir}/libmumble.so.%{version} $RPM_BUILD_ROOT%{_libdir}/%{name}/libmumble.so.1
ln -s %{_libdir}/libmumble.so.%{version} $RPM_BUILD_ROOT%{_libdir}/%{name}/libmumble.so.1.1

install -d $RPM_BUILD_ROOT%{_sysconfdir}/murmur/
install -pD scripts/murmur.ini.system $RPM_BUILD_ROOT%{_sysconfdir}/murmur/murmur.ini
ln -s ..%{_sysconfdir}/murmur/murmur.ini $RPM_BUILD_ROOT%{_sysconfdir}/%{name}-server.ini
install -pD %{SOURCE1} $RPM_BUILD_ROOT%{_initrddir}/murmur

install -d $RPM_BUILD_ROOT%{_datadir}/%{name}/
install -pD scripts/%{name}-overlay $RPM_BUILD_ROOT%{_bindir}/%{name}-overlay

#man pages
install -d $RPM_BUILD_ROOT%{_mandir}/man1/
install -pD man/murmurd.1 $RPM_BUILD_ROOT%{_mandir}/man1/
install -pD man/mumble* $RPM_BUILD_ROOT%{_mandir}/man1/
#install -pD -m0664 man/mumble-overlay.1 $RPM_BUILD_ROOT%{_mandir}/man1/mumble-overlay.1

#icons
install -d $RPM_BUILD_ROOT%{_datadir}/icons/%{name}
install -pD icons/%{name}.16x16.png $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/16x16/apps/%{name}.png
install -pD icons/%{name}.32x32.png $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/32x32/apps/%{name}.png
install -pD icons/%{name}.48x48.png $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/48x48/apps/%{name}.png
install -pD icons/%{name}.64x64.png $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/64x64/apps/%{name}.png

#logrotate
install -pD scripts/murmur.logrotate $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/murmur

# install desktop file
desktop-file-install --dir=$RPM_BUILD_ROOT%{_desktopdir} \
%{SOURCE2}

#install desktop file for mumble-overlay
#desktop-file-install --dir=$RPM_BUILD_ROOT%{_desktopdir} \
#%{SOURCE3}

# install the mumble protocol
install -pD scripts/%{name}.protocol $RPM_BUILD_ROOT%{_datadir}/kde4/services/%{name}.protocol

# murmur.conf
install -pD scripts/murmur.conf $RPM_BUILD_ROOT%{_sysconfdir}/dbus-1/system.d/murmur.conf

#dir for mumble-server.sqlite
install -d $RPM_BUILD_ROOT%{_localstatedir}/lib/mumble-server/

#log dir
install -d $RPM_BUILD_ROOT%{_localstatedir}/log/mumble-server/

#pid dir
install -d $RPM_BUILD_ROOT%{_localstatedir}/run/mumble-server/

%post
/sbin/ldconfig
touch --no-create %{_datadir}/icons/hicolor &>/dev/null ||:

%postun
/sbin/ldconfig
if [ $1 -eq 0 ] ; then
    touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%postun -n murmur
if [ $1 -ge 1 ] ; then
    %service murmur condrestart >/dev/null 2>&1 || :
fi

%posttrans
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null ||:


%clean
rm -rf $RPM_BUILD_ROOT

%preun -n murmur
if [ $1 = 0 ] ; then
	%service murmur stop > /dev/null 2>&1 || :
	/sbin/chkconfig --del murmur || :
fi

%post -n murmur
/sbin/chkconfig --add murmur || :


%files
%defattr(644,root,root,755)
%doc README README.Linux LICENSE CHANGES
%doc scripts/*.pl scripts/*%{name}-policy*
%doc scripts/*php scripts/qt.conf
%attr(755,root,root) %{_libdir}/libmumble.so*
%attr(755,root,root) %{_libdir}/%{name}/libmumble.so*
%attr(755,root,root) %{_bindir}/%{name}
#%attr(664,root,root) %{_datadir}/%{name}/*
%{_mandir}/man1/%{name}*
#%{_mandir}/man1/%{name}-overlay.1
%{_iconsdir}/hicolor/16x16/apps/%{name}.png
%{_iconsdir}/hicolor/32x32/apps/%{name}.png
%{_iconsdir}/hicolor/48x48/apps/%{name}.png
%{_iconsdir}/hicolor/64x64/apps/%{name}.png
%{_desktopdir}/%{name}.desktop
#%{_datadir}/hal/fdi/policy/20thirdparty/11-input-mumble-policy.fdi

%files -n murmur
%defattr(644,root,root,755)
%doc README README.Linux LICENSE CHANGES
#%attr(-,mumble-server,mumble-server) %{_sbindir}/murmur
%attr(-,mumble-server,mumble-server) %{_sbindir}/murmurd
%attr(-,mumble-server,mumble-server) %{_initrddir}/murmur
%attr(755,root,root) %{_sbindir}/%{name}-server
%config(noreplace) %attr(664,mumble-server,mumble-server) %{_sysconfdir}/murmur/murmur.ini
%config(noreplace) %attr(664,mumble-server,mumble-server) %{_sysconfdir}/mumble-server.ini
%{_mandir}/man1/murmurd.1*
%attr(664,root,root) /etc/logrotate.d/murmur
/etc/dbus-1/system.d/murmur.conf
%dir %attr(-,mumble-server,mumble-server) %{_localstatedir}/lib/mumble-server/
%dir %attr(-,mumble-server,mumble-server) %{_localstatedir}/log/mumble-server/
%dir %attr(-,mumble-server,mumble-server) %{_localstatedir}/run/mumble-server/

%files plugins
%defattr(644,root,root,755)
%{_libdir}/%{name}

%files overlay
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/%{name}-overlay
#%{_desktopdir}/%{name}-overlay.desktop

%files protocol
%defattr(644,root,root,755)
%{_datadir}/kde4/services/mumble.protocol
