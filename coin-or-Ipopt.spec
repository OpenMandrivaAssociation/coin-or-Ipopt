%global		_disable_ld_no_undefined	1
%global		module		Ipopt
%global		lmpi_f77	-lmpi_mpifh

Name:		coin-or-%{module}

Summary:	Interior Point OPTimizer
Version:	3.11.0
Release:	4%{?dist}
License:	EPL and GPLv2+
URL:		https://projects.coin-or.org/%{module}
Source0:	http://www.coin-or.org/download/pkgsource/%{module}/%{module}-%{version}.tgz
Source1:	%{name}.rpmlintrc
BuildRequires:	blas-devel
BuildRequires:	blacs-openmpi-devel
BuildRequires:	gcc-gfortran
BuildRequires:	doxygen
BuildRequires:	glpk-devel
BuildRequires:	graphviz
BuildRequires:	lapack-devel
BuildRequires:	libatlas-devel
BuildRequires:	MUMPS-devel
BuildRequires:	openmpi-devel
BuildRequires:	scalapack-openmpi-devel
BuildRequires:	openssh-clients
BuildRequires:	pkgconfig
BuildRequires:	readline-devel

# Properly handle DESTDIR
Patch0:		%{name}-pkgconfig.patch

# Install documentation in standard rpm directory
Patch1:		%{name}-docdir.patch

# Build with parallel mumps solver
Patch2:		%{name}-mumps.patch

# Correct underlink of libdl
Patch3:		%{name}-underlink.patch

%description
Ipopt (Interior Point OPTimizer, pronounced eye-pea-Opt) is a software
package for large-scale nonlinear optimization. It is designed to find
(local) solutions of mathematical optimization problems of the from

   min     f(x)
x in R^n

s.t.       g_L <= g(x) <= g_U
           x_L <=  x   <= x_U

where f(x): R^n --> R is the objective function, and g(x): R^n --> R^m are
the constraint functions. The vectors g_L and g_U denote the lower and upper
bounds on the constraints, and the vectors x_L and x_U are the bounds on
the variables x. The functions f(x) and g(x) can be nonlinear and nonconvex,
but should be twice continuously differentiable. Note that equality
constraints can be formulated in the above formulation by setting the
corresponding components of g_L and g_U to the same value.

%package	devel
Summary:	Development files for %{name}

Requires:	coin-or-CoinUtils-devel
Requires:	%{name}%{?_isa} = %{version}-%{release}

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%package	doc
Summary:	Documentation files for %{name}

Requires:	%{name} = %{version}-%{release}
BuildArch:	noarch

%description	doc
This package contains the documentation for %{name}.

%prep
%setup -q -n %{module}-%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

%build
mkdir bin; pushd bin; ln -sf %{_bindir}/ld.bfd ld; popd; export PATH=$PWD/bin:$PATH
%_openmpi_load
CFLAGS="%{optflags} -fuse-ld=bfd" \
CXXFLAGS="%{optflags} -fuse-ld=bfd" \
FFLAGS="%{optflags} -fuse-ld=bfd" \
%configure2_5x							\
	--with-mumps-lib="-ldmumps -L$MPI_LIB -lmpi -lscalapack -llapack -lmpiblacs %{lmpi_f77} -lmpiblacsF77init -lmpiblacsCinit -lmpi_cxx"	\
	--with-mumps-incdir=%{_includedir}/MUMPS

# Kill rpaths
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

# do not block waiting for input
echo 'LATEX_BATCHMODE = YES' >> doxydoc/doxygen.conf

make %{?_smp_mflags}						\
	CFLAGS="$CFLAGS -I$MPI_INCLUDE -DIPOPT_BUILD"		\
	CXXFLAGS="$CXXFLAGS -I$MPI_INCLUDE -DIPOPT_BUILD"	\
	all doxydoc

%install
export PATH=$PWD/bin:$PATH
make install DESTDIR=%{buildroot}
rm -f %{buildroot}%{_libdir}/*.la

cp -far doxydoc/html %{buildroot}%{_docdir}/%{name}

# https://projects.coin-or.org/Ipopt/ticket/75
%check
export PATH=$PWD/bin:$PATH
%_openmpi_load
LD_LIBRARY_PATH=%{buildroot}%{_libdir}:$LD_LIBRARY_PATH make test

%files
%dir %{_docdir}/%{name}
%doc %{_docdir}/%{name}/AUTHORS
%doc %{_docdir}/%{name}/ipopt*.txt
%doc %{_docdir}/%{name}/LICENSE
%doc %{_docdir}/%{name}/README
%{_libdir}/*.so.*

%files		devel
%{_includedir}/coin/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/*

%files		doc
%{_docdir}/%{name}/html

%changelog
* Mon Apr  7 2014 pcpa <paulo.cesar.pereira.de.andrade@gmail.com> - 3.11.0-4
- Correct files conflict (#1084893).

* Wed Aug  7 2013 pcpa <paulo.cesar.pereira.de.andrade@gmail.com> - 3.11.0-3
- Switch to unversioned docdir.
- Correct rawhide FTBFS (#992075).

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.11.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Sat May 11 2013 pcpa <paulo.cesar.pereira.de.andrade@gmail.com> - 3.11.0-1
- Update to latest upstream release.
- Adjust patches and build for sources now in toplevel directory.

* Thu May 9 2013 pcpa <paulo.cesar.pereira.de.andrade@gmail.com> - 3.10.4-1
- Update to latest upstream release.
- Switch to the new upstream tarballs without bundled dependencies.

* Sat Mar  2 2013 pcpa <paulo.cesar.pereira.de.andrade@gmail.com> - 3.10.3-2
- Remove ThirdParty directory.
- Make use of the MUMPS solver (#913152).
- Split html documentation in a doc package.

* Mon Jan 14 2013 pcpa <paulo.cesar.pereira.de.andrade@gmail.com> - 3.10.3-1
- Update to latest upstream release.

* Sat Jan 12 2013 pcpa <paulo.cesar.pereira.de.andrade@gmail.com> - 3.10.2-3
- Rename repackaged tarball.

* Sun Nov 18 2012 pcpa <paulo.cesar.pereira.de.andrade@gmail.com> - 3.10.2-2
- Rename package to coin-or-Ipopt.
- Do not package Thirdy party data or data without clean license.

* Sat Sep 29 2012 pcpa <paulo.cesar.pereira.de.andrade@gmail.com> - 3.10.2-1
- Initial coinor-Ipopt spec.
