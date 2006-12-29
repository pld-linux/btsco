#
# Conditional build:
%bcond_without	dist_kernel	# without kernel from distribution
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace utilities
%bcond_without	smp		# don't build SMP module
%bcond_with	verbose		# verbose build (V=1)
#
%define	rel	1
Summary:	Bluetooth-alsa Project
Summary(pl):	Projekt Bluetooth-alsa
Name:		btsco
Version:	0.5
Release:	%{rel}
License:	GPL
Group:		Applications/Sound
Source0:	http://dl.sourceforge.net/bluetooth-alsa/%{name}-%{version}.tgz
# Source0-md5:	d9fdd63a9e22ba839a41c8a9b89c2dda
Patch0:		%{name}-readme-pl.diff
URL:		http://sourceforge.net/projects/bluetooth-alsa/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build}
%endif
%if %{with userspace}
BuildRequires:	alsa-driver-devel >= 1.0.9-1
BuildRequires:	alsa-lib-devel >= 1.0.9-1
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	bluez-libs-devel >= 2.21-1
BuildRequires:	libao-devel >= 0.8.6-1
BuildRequires:	libtool
BuildRequires:	rpmbuild(macros) >= 1.330
%endif
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This project provides a way to use a bluetooth headset with Linux. We
do this currently by making an alsa kernel driver which uses bluez to
reach the headset. It works well enough now to get voice-quality audio
to and from most headsets.

%description -l pl
Dziêki temu oprogramowaniu mo¿na u¿ywaæ zestawów s³uchawkowych
Bluetooth Headset z Linuksem. Osi±gniêto to dziêki zbudowaniu alsowego
modu³u do j±dra, który to u¿ywa systemu bluez do komunikacji z takim
zestawem. Wspó³pracuje z wiêkszo¶ci± zestawów, ograniczeniem w
komunikacji jest czêsto urz±dzenie USB, które to mo¿e mieæ
nieobs³ugiwane czê¶ciowo protoko³y, wskazówka: hciconfig hciXXX
revision. W skrajnym wypadku mo¿na próbowaæ u¿yæ innego urz±dzenia
USB.

%package -n kernel%{_alt_kernel}-char-btsco
Summary:	Linux ALSA kernel driver for Bluetooth Headset
Summary(pl):	Sterownik ALSA do j±dra Linuksa dla Bluetooth Headset
Release:	%{rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod
Requires:	kernel%{_alt_kernel}-sound-alsa

%description -n kernel%{_alt_kernel}-char-btsco
Linux ALSA kernel driver for Bluetooth Headset named snd_bt_sco.

%description -n kernel%{_alt_kernel}-char-btsco -l pl
Sterownik ALSA do j±dra Linuksa dla Bluetooth Headset o nazwie
snd_bt_sco.

%package -n kernel%{_alt_kernel}-smp-char-btsco
Summary:	Linux ALSA kernel driver for Bluetooth Headset (SMP)
Summary(pl):	Sterownik ALSA do j±dra Linuksa dla Bluetooth Headset (SMP)
Release:	%{rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod
Requires:	kernel%{_alt_kernel}-smp-sound-alsa

%description -n kernel%{_alt_kernel}-smp-char-btsco
Linux ALSA kernel (SMP) driver for Bluetooth Headset named snd_bt_sco.

%description -n kernel%{_alt_kernel}-smp-char-btsco -l pl
Sterownik ALSA do j±dra Linuksa SMP dla Bluetooth Headset o nazwie
snd_bt_sco.

%prep
%setup -q
%patch0 -p1

%build
%if %{with userspace}
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
%configure

%{__make}
%endif

%if %{with kernel}
%build_kernel_modules -m snd-bt-sco -C kernel
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
install -d $RPM_BUILD_ROOT%{_bindir}

for file in avdtp/avtest sbc/rcplay sbc/sbcenc sbc/sbcinfo a2play btsco2 btsco ; do
	install $file $RPM_BUILD_ROOT%{_bindir}
done
%endif

%if %{with kernel}
%install_kernel_modules -m kernel/snd-bt-sco -d misc
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post -n kernel%{_alt_kernel}-char-btsco
%depmod %{_kernel_ver}
echo "after install this package, remember add lines like this:"
echo "alias snd-card-1 snd-bt-sco"
echo "alias sound-slot-1 snd-bt-sco"
echo "to %{_sysconfdir}/modprobe.conf"

%postun -n kernel%{_alt_kernel}-char-btsco
%depmod %{_kernel_ver}

%post -n kernel%{_alt_kernel}-smp-char-btsco
%depmod %{_kernel_ver}smp
echo "after install this package, remember add lines like this:"
echo "alias snd-card-1 snd-bt-sco"
echo "alias sound-slot-1 snd-bt-sco"
echo "to %{_sysconfdir}/modprobe.conf"

%postun -n kernel%{_alt_kernel}-smp-char-btsco
%depmod %{_kernel_ver}smp

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc README README.PL.txt
%attr(755,root,root) %{_bindir}/*
%endif

%if %{with kernel}
%files -n kernel%{_alt_kernel}-char-btsco
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/snd-bt-sco.ko.gz
%endif

%if %{with smp}
%files -n kernel%{_alt_kernel}-smp-char-btsco
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/misc/snd-bt-sco.ko.gz
%endif
