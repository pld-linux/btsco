#
# Conditional build:
%bcond_without	dist_kernel	# without kernel from distribution
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace utilities
%bcond_without	smp		# don't build SMP module
%bcond_with	verbose		# verbose build (V=1)
#
Summary:	Bluetooth-alsa Project
Summary(pl):	Projekt Bluetooth-alsa
Name:		btsco
Version:	0.4
%define	rel	1
Release:	%{rel}
License:	GPL
Group:		Applications/Sound
Source0:	http://dl.sourceforge.net/bluetooth-alsa/%{name}-%{version}.tar.gz
# Source0-md5:	3f46d45db6f0e399044ae6a31b1f23c7
Patch0:		%{name}-readme-pl.diff
URL:		http://sourceforge.net/projects/bluetooth-alsa/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libtool
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel-module-build}
%endif
%if %{with userspace}
BuildRequires:	alsa-driver-devel >= 1.0.9-1
BuildRequires:	alsa-lib-devel >= 1.0.9-1
BuildRequires:	bluez-libs-devel >= 2.21-1
BuildRequires:	libao-devel >= 0.8.6-1
%endif
ExclusiveArch:	%{ix86}
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

%package -n kernel-char-btsco
Summary:	Linux ALSA kernel driver for Bluetooth Headset
Summary(pl):	Sterownik ALSA do j±dra Linuksa dla Bluetooth Headset
Release:	%{rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod
Requires:	kernel-sound-alsa

%description -n kernel-char-btsco
Linux ALSA kernel driver for Bluetooth Headset named snd_bt_sco.

%description -n kernel-char-btsco -l pl
Sterownik ALSA do j±dra Linuksa dla Bluetooth Headset o nazwie
snd_bt_sco.

%package -n kernel-smp-char-btsco
Summary:	Linux ALSA kernel driver for Bluetooth Headset (SMP)
Summary(pl):	Sterownik ALSA do j±dra Linuksa dla Bluetooth Headset (SMP)
Release:	%{rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod
Requires:	kernel-smp-sound-alsa

%description -n kernel-smp-char-btsco
Linux ALSA kernel (SMP) driver for Bluetooth Headset named snd_bt_sco.

%description -n kernel-smp-char-btsco -l pl
Sterownik ALSA do j±dra Linuksa SMP dla Bluetooth Headset o nazwie
snd_bt_sco.

%prep
%setup -q
%patch0 -p1

%build
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__automake}
%configure

%if %{with userspace}
%{__make}
%endif

%if %{with kernel}
cd kernel
# kernel module(s)
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	rm -rf include
	install -d include/{linux,config}
	ln -sf %{_kernelsrcdir}/config-$cfg .config
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h include/linux/autoconf.h
	ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} include/asm
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg Module.symvers
	touch include/config/MARKER

	# patching/creating makefile(s) (optional)
	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		M=$PWD O=$PWD \
		%{?with_verbose:V=1}
	%{__make} -C %{_kernelsrcdir} modules \
		CC="%{__cc}" CPP="%{__cpp}" \
		M=$PWD O=$PWD \
		%{?with_verbose:V=1}
	for mod in *.ko; do
		mod=$(echo "$mod" | sed -e 's#\.ko##g')
		mv $mod.ko ../$mod-$cfg.ko
	done
done
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
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/misc
	%if %{without dist_kernel}
	for mod in *-nondist.ko; do
		nmod=$(echo "$mod" | sed -e 's#-nondist##g')
		pwd
		install $mod $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc/$nmod
	done
	%else
	for mod in *-up.ko; do
		nmod=$(echo "$mod" | sed -e 's#-up##g')
		pwd
		install $mod $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc/$nmod
	done
	%endif

	%if %{with smp}
	for mod in *-smp.ko; do
		nmod=$(echo "$mod" | sed -e 's#-smp##g')
		pwd
		install $mod $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/misc/$nmod
	done
	%endif
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post -n kernel-char-btsco
%depmod %{_kernel_ver}
echo "after install this package, remember add lines like this:"
echo "alias snd-card-1 snd-bt-sco"
echo "alias sound-slot-1 snd-bt-sco"
echo "to %{_sysconfdir}/modprobe.conf"

%postun -n kernel-char-btsco
%depmod %{_kernel_ver}

%post -n kernel-smp-char-btsco
%depmod %{_kernel_ver}
echo "after install this package, remember add lines like this:"
echo "alias snd-card-1 snd-bt-sco"
echo "alias sound-slot-1 snd-bt-sco"
echo "to %{_sysconfdir}/modprobe.conf"

%postun -n kernel-smp-char-btsco
%depmod %{_kernel_ver}

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc COPYING README README.PL.txt NEWS AUTHORS ChangeLog INSTALL
%attr(755,root,root) %{_bindir}/*
%endif

%if %{with kernel}
%files -n kernel-char-btsco
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/snd-bt-sco.ko.gz
%endif

%if %{with smp}
%files -n kernel-smp-char-btsco
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/misc/snd-bt-sco.ko.gz
%endif
