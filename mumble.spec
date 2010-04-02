
%define		qtver	4.6.2
%define		snap	20100401

Summary:	Voice chat software primarily intended for use while gaming
Name:		mumble
Version:	1.2.2
Release:	0.1
License:	BSD and Custom (see LICENSE)
Group:		Applications/Communications
Source0:	http://dl.sourceforge.net/mumble/%{name}-%{version}.tar.gz
# Source0-md5:	de30ee85170e183b66568b53b04c5727
# get it via: git clone git://mumble.git.sourceforge.net/gitroot/mumble/mumble
#Source0:	%{name}-%{version}-%{snap}.tar.gz
URL:		http://mumble.sourceforge.net/
Source1:	murmur.init
Source2:	%{name}.desktop
Source3:	%{name}-overlay.desktop
Patch0:		%{name}-compile-fix.patch
BuildRequires:	Ice-devel
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
BuildRequires:	protobuf-devel
BuildRequires:	qt4-build >= %{qtver}
BuildRequires:	qt4-qmake >= %{qtver}
BuildRequires:	speech-dispatcher-devel
BuildRequires:	speex-devel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Low-latency, high-quality voice communication for gamers. Includes
game linking, so voice from other players comes from the direction of
their characters, and has echo cancellation so the sound from your
loudspeakers won't be audible to other players.

%package server
Summary:	Mumble voice chat server
Group:		Applications/Communications
Requires:	QtSql-sqlite3 >= %{qtver}
Requires(post,preun):	/sbin/chkconfig

%description server
Murmur (also called mumble-server) is part of VoIP suite Mumble
primarily intended for gamers. Murmur is server part of suite.

%prep
%setup -q
%patch0 -p1

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

install -d $RPM_BUILD_ROOT{%{_sbindir},%{_bindir},%{_libdir},/etc/murmur}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install release/libmumble.so.1.2.2 $RPM_BUILD_ROOT%{_libdir}
install release/mumble* $RPM_BUILD_ROOT%{_bindir}
install release/murmurd $RPM_BUILD_ROOT%{_sbindir}
install scripts/murmur.ini $RPM_BUILD_ROOT/etc/murmur

%clean
rm -rf $RPM_BUILD_ROOT

%post   -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%post server
/sbin/chkconfig --add murmurd
%service murmurd restart "mumble server"

%preun server
if [ "$1" = "0" ]; then
	%service murmurd stop
	/sbin/chkconfig --del ejabberd
fi

%files
%defattr(644,root,root,755)
%doc README README.Linux LICENSE CHANGES
%attr(755,root,root) %{_bindir}/mumble
%attr(755,root,root) %{_bindir}/mumble11x
%attr(755,root,root) %{_libdir}/libmumble.so.1.2.2

%files server
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/murmurd
%dir /etc/murmur
/etc/murmur/murmur.ini
