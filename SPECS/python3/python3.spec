%global VER 3.11
%global with_gdb_hooks 1

# For some reason, Azure Linux throws all of various package macros into a single package, mariner-rpm-macros...?
%bcond macros 0

Summary:        A high-level scripting language
Name:           python3
Version:        3.11.7
Release:        2%{?dist}
License:        PSF
Vendor:         Microsoft Corporation
Distribution:   Mariner
Group:          System Environment/Programming
URL:            https://www.python.org/

Source0:        https://www.python.org/ftp/python/%{version}/Python-%{version}.tar.xz

%if %{with macros}
Source1:        macros.python
%endif

Patch0: cgi3.patch
Patch1: use-HMAC-SHA256-in-FIPS-mode.patch

BuildRequires:  bzip2-devel
BuildRequires:  expat-devel >= 2.1.0
BuildRequires:  libffi-devel >= 3.0.13
BuildRequires:  ncurses-devel
BuildRequires:  openssl-devel
BuildRequires:  pkg-config >= 0.28
BuildRequires:  readline-devel
BuildRequires:  sqlite-devel
BuildRequires:  util-linux-devel
BuildRequires:  xz-devel

Requires:       ncurses
Requires:       openssl
Requires:       %{name}-libs = %{version}-%{release}
Requires:       readline
Requires:       xz
Provides:       python
Provides:       python-sqlite
Provides:       python(abi)
Provides:       %{_bindir}/python
Provides:       /bin/python
Provides:       /bin/%{name}

%if 0%{?with_check}
BuildRequires:  iana-etc
BuildRequires:  tzdata
BuildRequires:  curl-devel
%endif

%description
The Python 3 package contains a new version of Python development environment.
Python 3 brings more efficient ways of handling dictionaries, better unicode
strings support, easier and more intuitive syntax, and removes the deprecated
code. It is incompatible with Python 2.x releases.

%package        libs
Summary:        The libraries for python runtime
Group:          Applications/System
Requires:       bzip2-libs
Requires:       (coreutils or coreutils-selinux)
Requires:       expat >= 2.1.0
Requires:       libffi >= 3.0.13
Requires:       ncurses
Requires:       sqlite-libs
Requires:       util-linux-libs
# python3-xml was provided as a separate package in Mariner 1.0
# We fold this into the libs subpackage in Mariner 2.0
Provides:       %{name}-xml = %{version}-%{release}

%description    libs
The python interpreter can be embedded into applications wanting to
use python as an embedded scripting language.  The python-libs package
provides the libraries needed for python 3 applications.

%package        curses
Summary:        Python module interface for NCurses Library
Group:          Applications/System
Requires:       ncurses
Requires:       %{name}-libs = %{version}-%{release}

%description    curses
The python3-curses package provides interface for ncurses library.

%package        devel
Summary:        The libraries and header files needed for Python development.
Group:          Development/Libraries
Requires:       expat-devel >= 2.1.0
Requires:       %{name} = %{version}-%{release}
%if %{with macros}
Requires:       %{name}-macros = %{version}-%{release}
%endif

%description    devel
The Python programming language's interpreter can be extended with
dynamically loaded extensions and can be embedded in other programs.
This package contains the header files and libraries needed to do
these types of tasks.

Install python-devel if you want to develop Python extensions.  The
python package will also need to be installed.  You'll probably also
want to install the python-docs package, which contains Python
documentation.

%package        tools
Summary:        A collection of development tools included with Python.
Group:          Development/Tools
Requires:       %{name} = %{version}-%{release}

%description    tools
The Python package includes several development tools that are used
to build python programs.

%package        pip
Summary:        The PyPA recommended tool for installing Python packages.
Group:          Development/Tools
Requires:       %{name} = %{version}-%{release}
BuildArch:      noarch

%description    pip
The PyPA recommended tool for installing Python packages.

%package        setuptools
Summary:        Download, build, install, upgrade, and uninstall Python packages.
Group:          Development/Tools
Requires:       %{name} = %{version}-%{release}
Provides:       python%{VER}dist(setuptools)
BuildArch:      noarch

%description    setuptools
setuptools is a collection of enhancements to the Python distutils that allow you to more easily build and distribute Python packages, especially ones that have dependencies on other packages.

%package        test
Summary:        Regression tests package for Python.
Group:          Development/Tools
Requires:       %{name} = %{version}-%{release}

%description test
The test package contains all regression tests for Python as well as the modules test.support and test.regrtest. test.support is used to enhance your tests while test.regrtest drives the testing suite.

%if %{with macros}
%package        macros
Summary:        Macros for Python packages.
Group:          Development/Tools
BuildArch:      noarch

%description    macros
This package contains the unversioned Python RPM macros, that most
implementations should rely on.
You should not need to install this package manually as the various
python-devel packages require it. So install a python-devel package instead.
%endif

%prep
%autosetup -p1 -n Python-%{version}

%build
export OPT="${CFLAGS}"
if [ %{_host} != %{_build} ]; then
  ln -sfv %{name} %{_bindir}/python
  export ac_cv_buggy_getaddrinfo=no
  export ac_cv_file__dev_ptmx=yes
  export ac_cv_file__dev_ptc=no
fi

%configure \
    --enable-shared \
    --with-system-expat \
    --with-system-ffi \
    --with-lto \
    --enable-optimizations \
    --with-dbmliborder=gdbm:ndbm \
    --with-ssl-default-suites=openssl \
    --with-builtin-hashlib-hashes=blake2

%make_build

%install
%make_install %{?_smp_mflags}
%{_fixperms} %{buildroot}/*

# Remove unused stuff
find %{buildroot}%{_libdir} -type f \( -name '*.pyc' -o \
                                       -name '*.pyo' -o \
                                       -name '*.exe' -o \
                                       -name '*.o' -o \
                                       -name '*__pycache__' \) -delete
rm %{buildroot}%{_bindir}/2to3
%if %{with macros}
mkdir -p %{buildroot}%{_rpmmacrodir}
install -m 644 %{SOURCE1} %{buildroot}%{_rpmmacrodir}
%endif
cp -p Tools/scripts/pathfix.py %{buildroot}%{_bindir}/pathfix%{VER}.py
ln -s ./pathfix%{VER}.py %{buildroot}%{_bindir}/pathfix.py

%if 0%{?__debug_package}
%if 0%{?with_gdb_hooks}
  DirHoldingGdbPy=%{_libdir}/debug%{_libdir}
  mkdir -p %{buildroot}$DirHoldingGdbPy
  PathOfGdbPy=$DirHoldingGdbPy/libpython%{VER}.so.1.0-%{version}-%{release}.%{_arch}.debug-gdb.py
  cp Tools/gdb/libpython.py %{buildroot}$PathOfGdbPy
%endif
%endif

%if 0%{?with_check}
%check
make %{?_smp_mflags} test
%endif

%post
ln -sfv %{_bindir}/%{name} %{_bindir}/python
/sbin/ldconfig

%postun
#we are handling the uninstall rpm
#in case of upgrade/downgrade we dont need any action
#as python will still be linked to python3
if [ $1 -eq 0 ] ; then
  if [ -f "%{_bindir}/python2" ]; then
    ln -sfv %{_bindir}/python2 %{_bindir}/python
  else
    rm -f %{_bindir}/python
  fi
fi
/sbin/ldconfig

%clean
rm -rf %{buildroot}/*

%files
%defattr(-, root, root)
%{_bindir}/pydoc*
%{_bindir}/%{name}
%{_bindir}/python%{VER}
%{_mandir}/*/*

%dir %{_libdir}/python%{VER}
%{_libdir}/python%{VER}/site-packages/README.txt

%exclude %{_libdir}/python%{VER}/ctypes/test
%exclude %{_libdir}/python%{VER}/distutils/tests
%exclude %{_libdir}/python%{VER}/idlelib/idle_test
%exclude %{_libdir}/python%{VER}/test
%exclude %{_libdir}/python%{VER}/lib-dynload/_ctypes_test.*.so

%files libs
%{_libdir}/libpython3.so
%{_libdir}/libpython%{VER}.so.1.0
%defattr(-, root, root)
%{_libdir}/python%{VER}
%exclude %{_libdir}/python%{VER}/lib2to3
%exclude %{_libdir}/python%{VER}/site-packages/
%exclude %{_libdir}/python%{VER}/ctypes/test
%exclude %{_libdir}/python%{VER}/distutils/tests
%exclude %{_libdir}/python%{VER}/idlelib/idle_test
%exclude %{_libdir}/python%{VER}/test
%exclude %{_libdir}/python%{VER}/lib-dynload/_ctypes_test.*.so
%exclude %{_libdir}/python%{VER}/curses
%exclude %{_libdir}/python%{VER}/lib-dynload/_curses*.so

%files  curses
%defattr(-, root, root, 755)
%{_libdir}/python%{VER}/curses/*
%{_libdir}/python%{VER}/lib-dynload/_curses*.so

%files devel
%defattr(-, root, root)
%{_includedir}/*
%{_libdir}/libpython%{VER}.so
%{_libdir}/pkgconfig/python-%{VER}.pc
%{_libdir}/pkgconfig/%{name}.pc
%{_bindir}/pathfix.py
%{_bindir}/pathfix%{VER}.py
%{_bindir}/%{name}-config
%{_bindir}/python%{VER}-config
%{_libdir}/pkgconfig/python-%{VER}-embed.pc
%{_libdir}/pkgconfig/%{name}-embed.pc

%exclude %{_bindir}/2to3*
%exclude %{_bindir}/idle*

%files tools
%defattr(-, root, root, 755)
%{_libdir}/python%{VER}/lib2to3
%{_bindir}/2to3-%{VER}
%exclude %{_bindir}/idle*

%files pip
%defattr(-, root, root, 755)
%{_libdir}/python%{VER}/site-packages/pip/*
%{_bindir}/pip*

%files setuptools
%defattr(-, root, root, 755)
%{_libdir}/python%{VER}/site-packages/distutils-precedence.pth
%{_libdir}/python%{VER}/site-packages/_distutils_hack/*
%{_libdir}/python%{VER}/site-packages/pkg_resources/*
%{_libdir}/python%{VER}/site-packages/setuptools/*
%{_libdir}/python%{VER}/site-packages/setuptools-*.dist-info/*

%files test
%defattr(-, root, root, 755)
%{_libdir}/python%{VER}/test/*

%if %{with macros}
%files macros
%defattr(-, root, root, 755)
%{_rpmmacrodir}/macros.python
%endif

%changelog
* Sun Feb  4 04:51:30 EST 2024 Dan Streetman <ddstreet@ieee.org> - 3.11.7-2
- update to python3.11

* Mon Dec 11 2023 Prashant S Chauhan <psinghchauha@vmware.com> 3.11.7-1
- Update to 3.11.7
* Sun Nov 19 2023 Shreenidhi Shedi <sshedi@vmware.com> 3.11.0-9
- Bump version as a part of openssl upgrade
* Fri Sep 08 2023 Prashant S Chauhan <psinghchauha@vmware.com> 3.11.0-8
- Add patch for multiprocessing library to use sha256  in FIPS mode
* Fri Jun 09 2023 Nitesh Kumar <kunitesh@vmware.com> 3.11.0-7
- Bump version as a part of ncurses upgrade to v6.4
* Wed Jan 25 2023 Shreenidhi Shedi <sshedi@vmware.com> 3.11.0-6
- Fix requires
* Thu Jan 12 2023 Shreenidhi Shedi <sshedi@vmware.com> 3.11.0-5
- Disable builtin hashes and use openssl backend for the same
* Wed Jan 11 2023 Oliver Kurth <okurth@vmware.com> 3.11.0-4
- bump release as part of sqlite update
* Fri Jan 06 2023 Oliver Kurth <okurth@vmware.com> 3.11.0-3
- bump version as a part of xz upgrade
* Tue Dec 20 2022 Guruswamy Basavaiah <bguruswamy@vmware.com> 3.11.0-2
- Bump release as a part of readline upgrade
* Mon Sep 19 2022 Prashant S Chauhan <psinghchauha@vmware.com> 3.11.0-1
- Update to 3.11
* Wed Oct 11 2023 Amrita Kohli <amritakohli@microsoft.com> - 3.9.14-8
- Patch for CVE-2023-24329

* Wed Sep 20 2023 Jon Slobodzian <joslobo@microsoft.com> - 3.9.14-7
- Recompile with stack-protection fixed gcc version (CVE-2023-4039)

* Thu Feb 02 2023 Daniel McIlvaney <damcilva@microsoft.com> - 3.9.14-6
- Patch CVE-2022-40897 in the bundled setuptools wheel

* Wed Dec 07 2022 Henry Beberman <henry.beberman@microsoft.com> - 3.9.14-5
- Add CVE-2022-42919 patch from upstream.

* Tue Dec 06 2022 Henry Beberman <henry.beberman@microsoft.com> - 3.9.14-4
- Add CVE-2022-45061 patch from upstream.

* Mon Dec 05 2022 Henry Beberman <henry.beberman@microsoft.com> - 3.9.14-3
- Add CVE-2022-37454 patch from upstream.
- Vulnerability not currently exposed because we use openssl sha3 implementation, but patching built-in sha3 regardless.

* Fri Oct 07 2022 Daniel McIlvaney <damcilva@microsoft.com> - 3.9.14-2
- Backport patch which allows cloud-init (among other programs) to use `import crypt` sucessfully when in FIPS mode

* Wed Sep 07 2022 Daniel McIlvaney <damcilva@microsoft.com> - 3.9.14-1
- Update to 3.9.14 to resolve security issues including CVE-2020-10735

* Wed Aug 31 2022 Henry Beberman <henry.beberman@microsoft.com> - 3.9.13-5
- Add CVE-2021-28861 patch from upstream

* Tue Aug 30 2022 Henry Beberman <henry.beberman@microsoft.com> - 3.9.13-4
- Add CVE-2015-20107 patch from upstream

* Tue Jul 12 2022 Olivia Crain <oliviacrain> - 3.9.13-3
- Update cgi3 patch to use versioned python shebang 

* Fri Jul 01 2022 Olivia Crain <oliviacrain@microsoft.com> - 3.9.13-2
- Remove Windows executables from pip, setuptools subpackages
- Add provides in the style of python39-%%{subpackage}, python3.9-%%{subpackage} for all packages except pip, setuptools 

* Mon Jun 20 2022 Olivia Crain <oliviacrain@microsoft.com> - 3.9.13-1
- Upgrade to latest maintenance release for the 3.9 series

* Tue Apr 26 2022 Olivia Crain <oliviacrain@microsoft.com> - 3.9.12-1
- Upgrade to latest maintenance release for the 3.9 series

* Tue Jan 25 2022 Thomas Crain <thcrain@microsoft.com> - 3.9.10-1
- Upgrade to latest bugfix release for the 3.9 series

* Mon Jan 10 2022 Muhammad Falak <mwani@microsoft.com> - 3.9.9-3
- Fix pip3 bootstrap which causes a build break in ptest

* Wed Dec 22 2021 Thomas Crain <thcrain@microsoft.com> - 3.9.9-2
- Use filtered flags when compiling extensions

* Mon Nov 29 2021 Thomas Crain <thcrain@microsoft.com> - 3.9.9-1
- Upgrade to latest release in 3.9 series
- Add profile guided optimization to configuration
- Fold xml subpackage into libs subpackage and add compatibility provides
- Align libpython*.so* file packaging with other distros
- Manually install pip/setuptools wheels
- Remove irrelevant patches
- License verified

* Fri Aug 12 2022 Shreenidhi Shedi <sshedi@vmware.com> 3.9.1-9
- Bump version as a part of sqlite upgrade
* Wed Aug 10 2022 Piyush Gupta <gpiyush@vmware.com> 3.9.1-8
- Handle EPERM error in crypt.py
* Tue May 10 2022 Shreenidhi Shedi <sshedi@vmware.com> 3.9.1-7
- Bump version as a part of libffi upgrade
* Wed Feb 02 2022 Shreenidhi Shedi <sshedi@vmware.com> 3.9.1-6
- Package python gdb hooks script
* Sat Aug 21 2021 Satya Naga Vasamsetty <svasamsetty@vmware.com> 3.9.1-5
- Bump up release for openssl
* Mon Aug 16 2021 Shreenidhi Shedi <sshedi@vmware.com> 3.9.1-4
- Fix python rpm macros
* Sat Mar 27 2021 Tapas Kundu <tkundu@vmware.com> 3.9.1-3
- Remove packaging exe files in python3-pip
* Sat Jan 16 2021 Shreenidhi Shedi <sshedi@vmware.com> 3.9.1-2
- Fix build with new rpm
* Fri Jan 08 2021 Tapas Kundu <tkundu@vmware.com> 3.9.1-1
- Update to 3.9.1
* Tue Oct 13 2020 Tapas Kundu <tkundu@vmware.com> 3.9.0-1
- Update to 3.9.0
* Wed Sep 30 2020 Gerrit Photon <photon-checkins@vmware.com> 3.8.6-1
- Automatic Version Bump
* Tue Sep 29 2020 Satya Naga Vasamsetty <svasamsetty@vmware.com> 3.8.5-4
- openssl 1.1.1
* Sun Aug 16 2020 Tapas Kundu <tkundu@vmware.com> 3.8.5-3
- Package %{_libdir}/python3.8/lib2to3 in tools
* Thu Aug 13 2020 Tapas Kundu <tkundu@vmware.com> 3.8.5-2
- Add macros subpackage
* Sun Jul 26 2020 Tapas Kundu <tkundu@vmware.com> 3.8.5-1
- Updated to 3.8.5 release

* Fri May 07 2021 Daniel Burgener <daburgen@microsoft.com> 3.7.10-3
- Remove coreutils dependency to remove circular dependency with libselinux

* Wed Apr 28 2021 Andrew Phelps <anphel@microsoft.com> - 3.7.10-2
- Add patch to fix test_ssl tests.

* Tue Apr 27 2021 Thomas Crain <thcrain@microsoft.com> - 3.7.10-1
- Merge the following releases from 1.0 to dev branch
- thcrain@microsoft.com, 3.7.9-1: Update to 3.7.9, the latest security release for 3.7
- thcrain@microsoft.com, 3.7.9-2: Patch CVE-2020-27619
- pawelw@microsoft.com, 3.7.9-3: Adding explicit runtime dependency on 'python3-xml' for the 'python3-setuptool' subpackage.
- nisamson@microsoft.com, 3.7.9-4: Patched CVE-2021-3177 with backported patch. Moved to autosetup.
- thcrain@microsoft.com, 3.7.10-1: Update to 3.7.10, the latest security release for 3.7, to fix CVE-2021-23336
-   Remove backported patches for CVE-2020-27619, CVE-2021-3177
- anphel@microsoft.com, 3.7.10-2: Add patch to fix test_ssl tests

* Tue Apr 20 2021 Henry Li <lihl@microsoft.com> - 3.7.7-11
- Provides python from python3

* Tue Mar 09 2021 Henry Li <lihl@microsoft.com> - 3.7.7-10
- Remove 2to3 binaries from python3-devel

* Wed Mar 03 2021 Henry Li <lihl@microsoft.com> - 3.7.7-9
- Fix python3-devel file section to include 2to3-3.7 and 2to3
- Provides python3-docs

* Fri Feb 05 2021 Joe Schmitt <joschmit@microsoft.com> - 3.7.7-8
- Turn off byte compilation since it requires this package to already be built and present.

* Mon Jan 04 2021 Ruying Chen <v-ruyche@microsoft.com> - 3.7.7-7
- Add python3 dist provides.

* Fri Dec 11 2020 Joe Schmitt <joschmit@microsoft.com> - 3.7.7-6
- Ship pathfix.py.
- pathfix.py spec changes imported from Fedora 32 (license: MIT)
- Provide python3dist(setuptools).

* Thu Oct 15 2020 Joe Schmitt <joschmit@microsoft.com> 3.7.7-5
- Add OPENSSL_NO_COMP flag to configuration.

* Mon Sep 28 2020 Joe Schmitt <joschmit@microsoft.com> 3.7.7-4
- Comment out check section to avoid unmet dependencies.

* Mon Sep 28 2020 Ruying Chen <v-ruyche@microsoft.com> 3.7.7-3
- Add Requires for python3-xml and python3-setuptools in python3-devel.

* Mon Jul 06 2020 Henry Beberman <henry.beberman@microsoft.com> 3.7.7-2
- Add BuildRequires for iana-etc and tzdata for check section.

* Wed Jun 10 2020 Paul Monson <paulmon@microsoft.com> 3.7.7-1
- Update to Python 3.7.7 to fix CVEs

* Fri Jul 17 2020 Tapas Kundu <tkundu@vmware.com> 3.7.5-3
- symlink python to python3
* Fri May 01 2020 Alexey Makhalov <amakhalov@vmware.com> 3.7.5-2
- -setuptools requires -xml.
* Sat Dec 07 2019 Tapas Kundu <tkundu@vmware.com> 3.7.5-1
- Updated to 3.7.5 release
- Linked /usr/bin/python to python3.
- While uninstalling link to python2 if available.
* Tue Nov 26 2019 Alexey Makhalov <amakhalov@vmware.com> 3.7.4-5
- Cross compilation support
* Tue Nov 05 2019 Tapas Kundu <tkundu@vmware.com> 3.7.4-4
- Fix for CVE-2019-17514
* Thu Oct 24 2019 Shreyas B. <shreyasb@vmware.com> 3.7.4-3
- Fixed makecheck errors.
* Wed Oct 23 2019 Tapas Kundu <tkundu@vmware.com> 3.7.4-2
- Fix conflict of libpython3.so
* Thu Oct 17 2019 Tapas Kundu <tkundu@vmware.com> 3.7.4-1
- Updated to patch release 3.7.4
- Fix CVE-2019-16935
* Thu May 21 2020 Suresh Babu Chalamalasetty <schalam@microsoft.com> 3.7.3-10
- Fix CVE-2019-16056.

* Wed May 20 2020 Nicolas Ontiveros <niontive@microsoft.com> 3.7.3-9
- Fix CVE-2020-8492.

* Wed May 20 2020 Paul Monson <paulmon@microsoft.com> 3.7.3-8
- Fix variable use.

* Sat May 09 2020 Nick Samson <nisamson@microsoft.com> - 3.7.3-7
- Added %%license line automatically

* Wed May 06 2020 Paul Monson <paulmon@microsoft.com> 3.7.3-6
- Replace unsupported TLS methods with a patch.

* Thu Apr 09 2020 Nicolas Ontiveros <niontive@microsoft.com> 3.7.3-5
- Remove toybox and only use coreutils for requires.

* Mon Nov 25 2019 Andrew Phelps <anphel@microsoft.com> 3.7.3-4
- Remove duplicate libpython3.so from devel package

* Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> 3.7.3-3
- Initial CBL-Mariner import from Photon (license: Apache2).

* Wed Sep 11 2019 Tapas Kundu <tkundu@vmware.com> 3.7.3-3
- Fix CVE-2019-16056
* Mon Jun 17 2019 Tapas Kundu <tkundu@vmware.com> 3.7.3-2
- Fix for CVE-2019-10160

* Mon Jun 10 2019 Tapas Kundu <tkundu@vmware.com> 3.7.3-1
- Update to Python 3.7.3 release

* Thu May 23 2019 Tapas Kundu <tkundu@vmware.com> 3.7.0-6
- Fix for CVE-2019-5010
- Fix for CVE-2019-9740

* Tue Mar 12 2019 Tapas Kundu <tkundu@vmware.com> 3.7.0-5
- Fix for CVE-2019-9636

* Mon Feb 11 2019 Taps Kundu <tkundu@vmware.com> 3.7.0-4
- Fix for CVE-2018-20406

* Fri Dec 21 2018 Tapas Kundu <tkundu@vmware.com> 3.7.0-3
- Fix for CVE-2018-14647

* Tue Dec 04 2018 Tapas Kundu <tkundu@vmware.com> 3.7.0-2
- Excluded windows installer from python3 libs packaging.

* Wed Sep 26 2018 Tapas Kundu <tkundu@vmware.com> 3.7.0-1
- Updated to version 3.7.0

* Mon Sep 18 2017 Alexey Makhalov <amakhalov@vmware.com> 3.6.1-9
- Requires coreutils or toybox
- Requires bzip2-libs

* Fri Sep 15 2017 Bo Gan <ganb@vmware.com> 3.6.1-8
- Remove devpts mount in check

* Mon Aug 28 2017 Dheeraj Shetty <dheerajs@vmware.com> 3.6.1-7
- Add pty for tests to pass

* Wed Jul 12 2017 Xiaolin Li <xiaolinl@vmware.com> 3.6.1-6
- Add python3-test package.

* Fri Jun 30 2017 Dheeraj Shetty <dheerajs@vmware.com> 3.6.1-5
- Remove the imaplib tests.

* Mon Jun 05 2017 Xiaolin Li <xiaolinl@vmware.com> 3.6.1-4
- Added pip, setuptools, xml, and curses sub packages.

* Sun Jun 04 2017 Bo Gan <ganb@vmware.com> 3.6.1-3
- Fix symlink and script

* Wed May 10 2017 Harish Udaiya Kumar <hudaiyakumar@vmware.com> 3.6.1-2
- Exclude idle3.

* Wed Apr 26 2017 Siju Maliakkal <smaliakkal@vmware.com> 3.6.1-1
- Updating to latest

* Fri Apr 14 2017 Alexey Makhalov <amakhalov@vmware.com> 3.5.3-3
- Python3-devel requires expat-devel.

* Thu Mar 23 2017 Xiaolin Li <xiaolinl@vmware.com> 3.5.3-2
- Provides /bin/python3.

* Tue Feb 28 2017 Xiaolin Li <xiaolinl@vmware.com> 3.5.3-1
- Updated to version 3.5.3.

* Fri Jan 20 2017 Dheeraj Shetty <dheerajs@vmware.com> 3.5.1-10
- Added patch to support Photon OS

* Tue Dec 20 2016 Xiaolin Li <xiaolinl@vmware.com> 3.5.1-9
- Move easy_install-3.5 to devel subpackage.

* Wed Nov 16 2016 Alexey Makhalov <ppadmavilasom@vmware.com> 3.5.1-8
- Use sqlite-{devel,libs}

* Thu Oct 27 2016 Anish Swaminathan <anishs@vmware.com> 3.5.1-7
- Patch for CVE-2016-5636

* Mon Oct 10 2016 ChangLee <changlee@vmware.com> 3.5.1-6
- Modified %check

* Tue May 24 2016 Priyesh Padmavilasom <ppadmavilasom@vmware.com> 3.5.1-5
- GA - Bump release of all rpms

* Wed May 04 2016 Anish Swaminathan <anishs@vmware.com> 3.5.1-4
- Edit scriptlets.

* Wed Apr 13 2016 Priyesh Padmavilasom <ppadmavilasom@vmware.com> 3.5.1-3
- update python to require python-libs

* Thu Apr 07 2016 Mahmoud Bassiouny <mbassiouny@vmware.com> 3.5.1-2
- Providing python3 binaries instead of the minor versions.

* Tue Feb 23 2016 Harish Udaiya Kumar <hudaiyakumar@vmware.com> 3.5.1-1
- Updated to version 3.5.1

* Wed Dec 09 2015 Anish Swaminathan <anishs@vmware.com> 3.4.3-3
- Edit post script.

* Mon Aug 17 2015 Vinay Kulkarni <kulkarniv@vmware.com> 3.4.3-2
- Remove python.o file, and minor cleanups.

* Wed Jul 1 2015 Vinay Kulkarni <kulkarniv@vmware.com> 3.4.3
- Add Python3 package to Photon.
