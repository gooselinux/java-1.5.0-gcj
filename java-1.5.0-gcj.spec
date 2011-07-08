# python support for aot-compile
%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

# convert an absolute path to a relative path.  each symbolic link is
# specified relative to the directory in which it is installed so that
# it will resolve properly within chrooted installations.
%define abs2rel %{__perl} -e 'use File::Spec; print File::Spec->abs2rel($ARGV[0], $ARGV[1])'

# resolve circular dependency between sinjdoc and java-1.5.0-gcj.
# define to 1 if sinjdoc has not been built yet.
%define bootstrap 0

# the plugin subpackage is disabled because libgcj's security
# infrastructure isn't ready to run untrusted applets.
%define enable_plugin 0

# the naming suffix for the gcc rpms we require (e.g., gcc4, libgcj4)
%define gccsuffix       %{nil}
# the version-release string for the gcj rpms we require
%define gccver          4.1.2-5
# the version string for the java-gcj-compat release we require
%define jgcver          1.0.79

# hard-code libdir on 64-bit architectures to make the 64-bit JDK
# simply be another alternative
%ifarch ppc64 s390x x86_64 sparc64
%define syslibdir        %{_prefix}/lib64
%define _libdir          %{_prefix}/lib
%else
%define syslibdir        %{_libdir}
%endif

# standard JPackage naming and versioning defines
%define origin          gcj%{gccsuffix}
%define priority        1500
%define javaver         1.5.0
%define buildver        0
%define name            java-%{javaver}-%{origin}

# standard JPackage directories and symbolic links
# make 64-bit JDKs just another alternative on 64-bit architectures
%define sdklnk          java-%{javaver}-%{origin}
%define jrelnk          jre-%{javaver}-%{origin}
%define sdkdir          %{name}-%{version}
%define jredir          %{sdkdir}/jre
%define sdkbindir       %{_jvmdir}/%{sdklnk}/bin
%define jrebindir       %{_jvmdir}/%{jrelnk}/bin
%define jvmjardir       %{_jvmjardir}/%{name}-%{version}

%if %{enable_plugin}
%define plugindir       %{_libdir}/mozilla/plugins
%endif

%define debug_package %{nil}

Name:    %{name}
Version: %{javaver}.%{buildver}
Release: 29.1%{?dist}
Summary: JPackage runtime compatibility layer for GCJ
Group:   Development/Languages
# The LICENSE file has the classpath exception, but nothing in this package
# seems to use or even need it.
License: GPLv2+
URL:     http://sources.redhat.com/rhug/java-gcj-compat.html
Source0: ftp://sources.redhat.com/pub/rhug/java-gcj-compat-%{jgcver}.tar.gz
Source1: javadoc-workaround.patch

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

# required to calculate gcj binary's path to encode in aotcompile.py
# and rebuild-gcj-db
BuildRequires: gcc%{gccsuffix}-java >= %{gccver}
BuildRequires: libgcj%{gccsuffix}-src >= %{gccver}
# required for cacerts generation
%ifnarch %{ix86}
BuildRequires: openssl
%else
# work around bug #500314
BuildRequires: openssl-devel
%endif
BuildRequires: python-devel
%if ! %{bootstrap}
# required for javadoc
BuildRequires: java-1.6.0-openjdk-devel
%endif
BuildRequires: unzip

# required for tools and libgcj.jar
Requires:         libgcj%{gccsuffix} >= %{gccver}
# required for directory structures
Requires:         jpackage-utils >= 1.7.3
# required for java.security symlink.  also ensures that the proper
# libgcj is installed on multilib systems.
Requires:         %{syslibdir}/security/classpath.security
%if ! %{bootstrap}
# required for javadoc symlink
Requires:         sinjdoc
%endif
# post requires alternatives to install tool alternatives
Requires(post):   %{_sbindir}/alternatives
# post requires gij to retrieve gcc version
Requires(post):   %{_bindir}/gij%{gccsuffix}
# post rebuilds the gcj database
Requires(post):   %{_bindir}/rebuild-gcj-db
# rebuild-gcj-db requires gcj-dbtool
Requires(post):   %{_bindir}/gcj-dbtool%{gccsuffix}
# rebuild-gcj-db requires findutils
Requires(post):   findutils
# postun requires alternatives to uninstall tool alternatives
Requires(postun): %{_sbindir}/alternatives
# postun requires gij to retrieve gcc version
Requires(postun): %{_bindir}/gij%{gccsuffix}
# postun rebuilds the gcj database
Requires(postun): %{_bindir}/rebuild-gcj-db
# rebuild-gcj-db requires gcj-dbtool
Requires(postun): %{_bindir}/gcj-dbtool%{gccsuffix}
# rebuild-gcj-db requires findutils
Requires(postun): findutils
# triggerin requires alternatives to install tool alternatives
Requires(triggerin): %{_sbindir}/alternatives
# triggerin requires gij to retrieve gcc version
Requires(triggerin): %{_bindir}/gij%{gccsuffix}
# triggerin requires perl for abs2rel
Requires(triggerin): perl

# standard JPackage base provides
Provides: jre-%{javaver}-%{origin} = %{version}-%{release}
Provides: jre-%{origin} = %{version}-%{release}
Provides: jre-%{javaver} = %{version}-%{release}
Provides: java-%{javaver} = %{version}-%{release}
Provides: jre = %{javaver}
Provides: java-%{origin} = %{version}-%{release}
Provides: java = %{javaver}
# libgcj provides, translated to JPackage provides
Provides: jaas = %{version}-%{release}
Provides: jce = %{version}-%{release}
Provides: jdbc-stdext = %{version}-%{release}
Provides: jdbc-stdext = 3.0
Provides: jndi = %{version}-%{release}
Provides: jndi-cos = %{version}-%{release}
Provides: jndi-dns = %{version}-%{release}
Provides: jndi-ldap = %{version}-%{release}
Provides: jndi-rmi = %{version}-%{release}
Provides: jsse = %{version}-%{release}
Provides: java-sasl = %{version}-%{release}
Provides: jaxp_parser_impl = %{version}-%{release}
# java-gcj-compat base provides
Provides: java-gcj-compat = %{jgcver}
Provides: java-1.4.2-gcj-compat > 1.4.2.0-40jpp.111

Obsoletes: java-1.4.2-gcj-compat <= 1.4.2.0-40jpp.111
Obsoletes: gnu-crypto <= 2.1.0-2jpp.1
Obsoletes: gnu-crypto-sasl-jdk1.4 <= 2.1.0-2jpp.1
Obsoletes: jessie <= 1.0.1-7

%description
This package installs directory structures, shell scripts and symbolic
links to simulate a JPackage-compatible runtime environment with GCJ.

%package devel
Summary: JPackage development compatibility layer for GCJ
Group:   Development/Tools

# FIXME: require libgcj-src for tools.jar symlink
Requires:         libgcj%{gccsuffix}-src >= %{gccver}
# require base package
Requires:         %{name} = %{version}-%{release}
# require eclipse-ecj for ecj binary
Requires:         eclipse-ecj >= 3.2.1
# require python for aot-compile
Requires:         python
# require gcc-java for gjavah binary
Requires:         gcc%{gccsuffix}-java >= %{gccver}
# post requires alternatives to install tool alternatives
Requires(post):   %{_sbindir}/alternatives
# post requires gcj to retrieve gcj header file locations
Requires(post):   %{_bindir}/gcj%{gccsuffix}
# postun requires alternatives to uninstall tool alternatives
Requires(postun): %{_sbindir}/alternatives
# triggerin requires gij to retrieve gcc version
Requires(triggerin): %{_bindir}/gij%{gccsuffix}
# triggerin requires gcj to retrieve gcj header file locations
Requires(triggerin): %{_bindir}/gcj%{gccsuffix}
# triggerin requires perl for abs2rel
Requires(triggerin): perl

# standard JPackage devel provides
Provides: java-sdk-%{javaver}-%{origin} = %{version}
Provides: java-sdk-%{javaver} = %{version}
Provides: java-sdk-%{origin} = %{version}
Provides: java-sdk = %{javaver}
Provides: java-%{javaver}-devel = %{version}
Provides: java-devel-%{origin} = %{version}
Provides: java-devel = %{javaver}
# java-gcj-compat devel provides
Provides: java-gcj-compat-devel = %{jgcver}
Provides: java-1.4.2-gcj-compat-devel > 1.4.2.0-40jpp.111

Obsoletes: java-1.4.2-gcj-compat-devel <= 1.4.2.0-40jpp.111

%description devel
This package installs directory structures, shell scripts and symbolic
links to simulate a JPackage-compatible development environment with
GCJ.

%package src
Summary: Source files for libgcj
Group:   Development/Libraries

Requires:       %{name} = %{version}-%{release}
Requires:       libgcj%{gccsuffix}-src >= %{gccver}
# post requires gij to retrieve gcc version
Requires(post): %{_bindir}/gij%{gccsuffix}
# triggerin requires gij to retrieve gcc version
Requires(triggerin): %{_bindir}/gij%{gccsuffix}
# triggerin requires perl for abs2rel
Requires(triggerin): perl

# java-gcj-compat src provides
Provides: java-1.4.2-gcj-compat-src > 1.4.2.0-40jpp.111

Obsoletes: java-1.4.2-gcj-compat-src <= 1.4.2.0-40jpp.111

%description src
This package installs a src.zip symbolic link that points to a
specific version of the libgcj sources.

%if ! %{bootstrap}
%package javadoc
Summary: API documentation for libgcj
Group:   Documentation

# require base package
Requires: %{name} = %{version}-%{release}

# standard JPackage javadoc provides
Provides: java-javadoc = %{version}-%{release}
Provides: java-%{javaver}-javadoc = %{version}-%{release}
# java-gcj-compat javadoc provides
Provides: java-1.4.2-gcj-compat-javadoc > 1.4.2.0-40jpp.111

Obsoletes: java-1.4.2-gcj-compat-javadoc <= 1.4.2.0-40jpp.111
Obsoletes: gnu-crypto-javadoc <= 2.1.0-2jpp.1

%description javadoc
This package installs Javadoc API documentation for libgcj.
%endif

%if %{enable_plugin}
%package plugin
Summary: Web browser plugin that handles applets
Group:   Applications/Internet

# require base package
Requires:         %{name} = %{version}-%{release}
# require libgcj for plugin shared object
Requires:         libgcj%{gccsuffix} >= %{gccver}
# require Mozilla plugin directory
Requires:         %{plugindir}
# post requires gij to retrieve gcc version
Requires(post):   %{_bindir}/gij%{gccsuffix}
# post requires alternatives to install plugin alternative
Requires(post):   %{_sbindir}/alternatives
# post requires Mozilla plugin directory
Requires(post):   %{plugindir}
# postun requires gij to retrieve gcc version
Requires(postun): %{_bindir}/gij%{gccsuffix}
# postun requires alternatives to uninstall plugin alternative
Requires(postun): %{_sbindir}/alternatives
# triggerin requires gij to retrieve gcc version
Requires(triggerin): %{_bindir}/gij%{gccsuffix}
# triggerin requires alternatives to install plugin alternative
Requires(triggerin): %{_sbindir}/alternatives

# standard JPackage plugin provides
Provides: java-plugin = %{javaver}
Provides: java-%{javaver}-plugin = %{version}
# java-gcj-compat plugin provides
Provides: java-1.4.2-gcj-compat-plugin > 1.4.2.0-40jpp.111

Obsoletes: java-1.4.2-gcj-compat-plugin <= 1.4.2.0-40jpp.111

%description plugin
This package installs a symbolic link to gcjwebplugin, a Mozilla
plugin for applets.
%endif

%prep
%setup -q -n java-gcj-compat-%{jgcver}

%build
# Print kernel version in logs.
uname -a
%configure --disable-symlinks --with-arch-directory=%{_arch} \
  --with-os-directory=linux \
  --with-security-directory=%{_sysconfdir}/java/security/security.d
make

# the python compiler encodes the source file's timestamp in the .pyc
# and .pyo headers.  since aotcompile.py is generated by configure,
# its timestamp will differ from build to build.  this causes multilib
# conflicts.  we work around this by setting aotcompile.py's timestamp
# to equal aotcompile.py.in's timestamp. (205216)
touch --reference=aotcompile.py.in aotcompile.py

%install
rm -rf $RPM_BUILD_ROOT

make DESTDIR=$RPM_BUILD_ROOT install

# extensions handling
install -dm 755 $RPM_BUILD_ROOT%{jvmjardir}
pushd $RPM_BUILD_ROOT%{jvmjardir}
  RELATIVE=$(%{abs2rel} %{_jvmdir}/%{jredir}/lib %{jvmjardir})
  for jarname in jaas jce jdbc-stdext jndi jndi-cos jndi-dns \
    jndi-ldap jndi-rmi jsse sasl
  do
    ln -s $RELATIVE/$jarname.jar $jarname-%{version}.jar
  done
  for jar in *-%{version}.jar
  do
    ln -sf ${jar} $(echo $jar | sed "s|-%{version}.jar|-%{javaver}.jar|g")
    ln -sf ${jar} $(echo $jar | sed "s|-%{version}.jar|.jar|g")
  done
popd

# security directory and provider list
install -dm 755 $RPM_BUILD_ROOT%{_jvmdir}/%{jredir}/lib/security
pushd $RPM_BUILD_ROOT%{_jvmdir}/%{jredir}/lib/security
  RELATIVE=$(%{abs2rel} %{syslibdir}/security \
    %{_jvmdir}/%{jredir}/lib/security)
  ln -sf $RELATIVE/classpath.security java.security
popd
# default security providers, provided by libgcj
install -dm 755 $RPM_BUILD_ROOT%{_sysconfdir}/java/security/security.d
for provider in \
  1000-gnu.java.security.provider.Gnu \
  1001-gnu.javax.crypto.jce.GnuCrypto \
  1002-gnu.javax.crypto.jce.GnuSasl \
  1003-gnu.javax.net.ssl.provider.Jessie \
  1004-gnu.javax.security.auth.callback.GnuCallbacks
do
  cat > $RPM_BUILD_ROOT%{_sysconfdir}/java/security/security.d/$provider << EOF
# This file's contents are ignored.  Its name, of the form
# <priority>-<provider name>, is used by post and postun scripts to
# rebuild the list of security providers in libgcj's
# classpath.security file.
EOF
done
# cacerts
%{__perl} generate-cacerts.pl
install -m 644 cacerts $RPM_BUILD_ROOT%{_jvmdir}/%{jredir}/lib/security

# versionless symbolic links
pushd $RPM_BUILD_ROOT%{_jvmdir}
   ln -s %{jredir} %{jrelnk}
   ln -s %{sdkdir} %{sdklnk}
popd
pushd $RPM_BUILD_ROOT%{_jvmjardir}
   ln -s %{sdkdir} %{jrelnk}
   ln -s %{sdkdir} %{sdklnk}
popd

# classmap database directory
install -dm 755 $RPM_BUILD_ROOT%{syslibdir}/gcj

%if ! %{bootstrap}
# build and install API documentation
install -dm 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}
pushd $RPM_BUILD_ROOT%{_javadocdir}
  ln -s %{name} java
popd
mkdir docsbuild
pushd docsbuild
  GIJ_VERSION=$(gij%{gccsuffix} --version | head -n 2 | tail -n 1 \
    | awk '{ print $5 }')
  echo ==== CHECK ZIP ====
  unzip -tq /usr/share/java/src-$GIJ_VERSION.zip || :
  echo ==== END CHECK ZIP ====
  if unzip -tq /usr/share/java/src-$GIJ_VERSION.zip
  then
    fastjar xvf /usr/share/java/src-$GIJ_VERSION.zip
    rm -rf gnu
    patch -p0 < %{SOURCE1}
    find ./ -name \*.java | xargs -n 1 dirname | sort | uniq \
      | sed -e "s/\.\///" | sed -e "s/\//\./" \
      | sed -e "s/\//\./" | sed -e "s/\//\./" \
      | sed -e "s/\//\./" | sed -e "s/\//\./" \
      | xargs javadoc -quiet \
      -d $RPM_BUILD_ROOT%{_javadocdir}/%{name} \
      -encoding UTF-8 -breakiterator \
      -linksource -splitindex -doctitle "GNU libgcj $GIJ_VERSION" \
      -windowtitle "GNU libgcj $GIJ_VERSION Documentation"
  else
    # Work around https://bugzilla.redhat.com/show_bug.cgi?id=404981
    touch $RPM_BUILD_ROOT%{_javadocdir}/%{name}/package-list
  fi
popd
%endif

# amd64 compatibility link
%ifarch x86_64
pushd $RPM_BUILD_ROOT%{_jvmdir}/%{jredir}/lib
  ln -s %{_arch} amd64
popd
%endif

# install operating system include directory
install -dm 755 $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}/include/linux

# install libjvm.so directories
install -dm 755 $RPM_BUILD_ROOT%{_jvmdir}/%{jredir}/lib/%{_arch}/client
install -dm 755 $RPM_BUILD_ROOT%{_jvmdir}/%{jredir}/lib/%{_arch}/server

# install tools.jar directory
install -dm 755 $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}/lib

touch $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}/include/jawt.h
touch $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}/include/jni.h
touch $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}/include/linux/jawt_md.h
touch $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}/include/linux/jni_md.h
touch $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}/lib/tools.jar
touch $RPM_BUILD_ROOT%{_jvmdir}/%{jredir}/lib/%{_arch}/libjawt.so
touch $RPM_BUILD_ROOT%{_jvmdir}/%{jredir}/lib/%{_arch}/client/libjvm.so
touch $RPM_BUILD_ROOT%{_jvmdir}/%{jredir}/lib/%{_arch}/server/libjvm.so
touch $RPM_BUILD_ROOT%{_jvmdir}/%{jredir}/lib/rt.jar
touch $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}/src.zip

pushd $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}/jre/lib
  for jarname in jaas jce jdbc-stdext jndi jndi-cos jndi-dns \
    jndi-ldap jndi-rmi jsse sasl
  do
    ln -s rt.jar $jarname.jar
  done
popd

%clean
rm -rf $RPM_BUILD_ROOT

%post
alternatives \
  --install %{_bindir}/java java %{jrebindir}/java %{priority} \
  --slave %{_jvmdir}/jre          jre          %{_jvmdir}/%{jrelnk} \
  --slave %{_jvmjardir}/jre       jre_exports  %{_jvmjardir}/%{jrelnk} \
  --slave %{_bindir}/keytool      keytool      %{jrebindir}/keytool \
  --slave %{_bindir}/rmiregistry  rmiregistry  %{jrebindir}/rmiregistry

alternatives \
  --install %{_jvmdir}/jre-%{origin} \
  jre_%{origin} %{_jvmdir}/%{jrelnk} %{priority} \
  --slave %{_jvmjardir}/jre-%{origin} \
  jre_%{origin}_exports %{_jvmjardir}/%{jrelnk}

alternatives \
  --install %{_jvmdir}/jre-%{javaver} \
  jre_%{javaver} %{_jvmdir}/%{jrelnk} %{priority} \
  --slave %{_jvmjardir}/jre-%{javaver} \
  jre_%{javaver}_exports %{_jvmjardir}/%{jrelnk}

GIJ_VERSION=$(gij%{gccsuffix} --version | head -n 2 | tail -n 1 \
  | awk '{ print $5 }')

# jaxp_parser_impl
alternatives --install %{_javadir}/jaxp_parser_impl.jar \
  jaxp_parser_impl %{_javadir}/libgcj-$GIJ_VERSION.jar 20

{
  # Rebuild the list of security providers in classpath.security.
  # This used to be a standalone script, rebuild-security-providers,
  # provided by the Fedora version of jpackage-utils.  Now it is
  # inlined here and removed from Fedora's jpackage-utils for
  # compatibility with jpackage.org's jpackage-utils.  See:
  # https://bugzilla.redhat.com/show_bug.cgi?id=260161
  suffix=security/classpath.security
  secfiles="/usr/lib/$suffix /usr/lib64/$suffix"

  for secfile in $secfiles
  do
    # check if this classpath.security file exists
    [ -f "$secfile" ] || continue

    sed -i '/^security\.provider\./d' "$secfile"

    count=0
    for provider in $(ls /etc/java/security/security.d)
    do
      count=$((count + 1))
      echo "security.provider.${count}=${provider#*-}" >> "$secfile"
    done
  done
} || :

if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi

%triggerin -- libgcj%{gccsuffix} >= %{gccver}
{
  GIJ_VERSION=$(gij%{gccsuffix} --version | head -n 2 | tail -n 1 \
    | awk '{ print $5 }')

  # jaxp_parser_impl
  alternatives --install %{_javadir}/jaxp_parser_impl.jar \
    jaxp_parser_impl \
    %{_javadir}/libgcj-$GIJ_VERSION.jar 20

  # rt.jar
  RELATIVE=$(%{abs2rel} %{_javadir} %{_jvmdir}/%{sdkdir}/jre/lib)
  ln -sf \
    $RELATIVE/libgcj-$GIJ_VERSION.jar \
    %{_jvmdir}/%{sdkdir}/jre/lib/rt.jar

  # libjawt.so
  RELATIVE=$(%{abs2rel} %{syslibdir}/gcj-$GIJ_VERSION \
    %{_jvmdir}/%{jredir}/lib/%{_arch})
  ln -sf $RELATIVE/libjawt.so \
    %{_jvmdir}/%{jredir}/lib/%{_arch}/libjawt.so

  # libjvm.so
  RELATIVE=$(%{abs2rel} %{syslibdir}/gcj-$GIJ_VERSION \
    %{_jvmdir}/%{jredir}/lib/%{_arch}/client)
  ln -sf $RELATIVE/libjvm.so \
    %{_jvmdir}/%{jredir}/lib/%{_arch}/client/libjvm.so
  RELATIVE=$(%{abs2rel} %{syslibdir}/gcj-$GIJ_VERSION \
    %{_jvmdir}/%{jredir}/lib/%{_arch}/server)
  ln -sf $RELATIVE/libjvm.so \
    %{_jvmdir}/%{jredir}/lib/%{_arch}/server/libjvm.so
} || :

%postun
if [ $1 -eq 0 ]
then
  GIJ_VERSION=$(gij%{gccsuffix} --version | head -n 2 | tail -n 1 \
    | awk '{ print $5 }')
  alternatives --remove java %{jrebindir}/java
  alternatives --remove jre_%{origin} %{_jvmdir}/%{jrelnk}
  alternatives --remove jre_%{javaver} %{_jvmdir}/%{jrelnk}
  alternatives --remove jaxp_parser_impl \
    %{_javadir}/libgcj-$GIJ_VERSION.jar
fi

{
  # Rebuild the list of security providers in classpath.security
  suffix=security/classpath.security
  secfiles="/usr/lib/$suffix /usr/lib64/$suffix"

  for secfile in $secfiles
  do
    # check if this classpath.security file exists
    [ -f "$secfile" ] || continue

    sed -i '/^security\.provider\./d' "$secfile"

    count=0
    for provider in $(ls /etc/java/security/security.d)
    do
      count=$((count + 1))
      echo "security.provider.${count}=${provider#*-}" >> "$secfile"
    done
  done
} || :

if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi

%post devel
alternatives \
  --install %{_bindir}/javac javac %{sdkbindir}/javac %{priority} \
  --slave %{_jvmdir}/java         java_sdk          %{_jvmdir}/%{sdklnk} \
  --slave %{_jvmjardir}/java      java_sdk_exports  %{_jvmjardir}/%{sdklnk} \
  --slave %{_bindir}/javadoc      javadoc           %{sdkbindir}/javadoc \
  --slave %{_bindir}/javah        javah             %{sdkbindir}/javah \
  --slave %{_bindir}/jar          jar               %{sdkbindir}/jar \
  --slave %{_bindir}/jarsigner    jarsigner         %{sdkbindir}/jarsigner \
  --slave %{_bindir}/appletviewer appletviewer      %{sdkbindir}/appletviewer \
  --slave %{_bindir}/rmic         rmic              %{sdkbindir}/rmic

alternatives \
  --install %{_jvmdir}/java-%{origin} \
  java_sdk_%{origin} %{_jvmdir}/%{sdklnk} %{priority} \
  --slave %{_jvmjardir}/java-%{origin} \
  java_sdk_%{origin}_exports %{_jvmjardir}/%{sdklnk}

alternatives \
  --install %{_jvmdir}/java-%{javaver} \
  java_sdk_%{javaver} %{_jvmdir}/%{sdklnk} %{priority} \
  --slave %{_jvmjardir}/java-%{javaver} \
  java_sdk_%{javaver}_exports %{_jvmjardir}/%{sdklnk}

# gcc-java requires libgcj-devel which provides jni.h
%triggerin devel -- gcc%{gccsuffix}-java >= %{gccver}
{
  GIJ_VERSION=$(gij%{gccsuffix} --version | head -n 2 | tail -n 1 \
    | awk '{ print $5 }')

  # tools.jar
  RELATIVE=$(%{abs2rel} %{_javadir} %{_jvmdir}/%{sdkdir}/lib)
  ln -sf \
    $RELATIVE/libgcj-tools-$GIJ_VERSION.jar \
    %{_jvmdir}/%{sdkdir}/lib/tools.jar

  # create symbolic links to headers in gcj's versioned directory
  for headername in jawt jni
  do
    DIRECTORY=$(dirname $(gcj%{gccsuffix} \
      -print-file-name=include/$headername.h))
    RELATIVE=$(%{abs2rel} $DIRECTORY %{_jvmdir}/%{sdkdir}/include)
    ln -sf $RELATIVE/$headername.h \
      %{_jvmdir}/%{sdkdir}/include/$headername.h
  done
  for headername in jawt_md jni_md
  do
    DIRECTORY=$(dirname $(gcj%{gccsuffix} \
      -print-file-name=include/$headername.h))
    RELATIVE=$(%{abs2rel} $DIRECTORY %{_jvmdir}/%{sdkdir}/include/linux)
    ln -sf $RELATIVE/$headername.h \
      %{_jvmdir}/%{sdkdir}/include/linux/$headername.h
  done
} || :

%postun devel
if [ $1 -eq 0 ]
then
  alternatives --remove javac %{sdkbindir}/javac
  alternatives --remove java_sdk_%{origin} %{_jvmdir}/%{sdklnk}
  alternatives --remove java_sdk_%{javaver} %{_jvmdir}/%{sdklnk}
fi

%triggerin src -- libgcj%{gccsuffix}-src >= %{gccver}
{
  GIJ_VERSION=$(gij%{gccsuffix} --version | head -n 2 | tail -n 1 \
    | awk '{ print $5 }')
  RELATIVE=$(%{abs2rel} %{_javadir} %{_jvmdir}/%{sdkdir})
  ln -sf \
    $RELATIVE/src-$GIJ_VERSION.zip \
    %{_jvmdir}/%{sdkdir}/src.zip
} || :

%if %{enable_plugin}
%triggerin plugin -- libgcj%{gccsuffix} >= %{gccver}
{
  GIJ_VERSION=$(gij%{gccsuffix} --version | head -n 2 | tail -n 1 \
    | awk '{ print $5 }')
  alternatives --install %{plugindir}/libjavaplugin.so \
    libjavaplugin.so %{syslibdir}/gcj-$GIJ_VERSION/libgcjwebplugin.so \
    %{priority}
} || :

%postun plugin
if [ $1 -eq 0 ]
then
  GIJ_VERSION=$(gij%{gccsuffix} --version | head -n 2 | tail -n 1 \
    | awk '{ print $5 }')
  alternatives --remove libjavaplugin.so \
    %{syslibdir}/gcj-$GIJ_VERSION/libgcjwebplugin.so
fi
%endif

%files
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog COPYING LICENSE README
%dir %{_jvmdir}/%{sdkdir}
%dir %{_jvmdir}/%{jredir}
%dir %{_jvmdir}/%{jredir}/bin
%dir %{_jvmdir}/%{jredir}/lib
%dir %{_jvmdir}/%{jredir}/lib/%{_arch}
%dir %{_jvmdir}/%{jredir}/lib/%{_arch}/client
%dir %{_jvmdir}/%{jredir}/lib/%{_arch}/server
%dir %{_jvmdir}/%{jredir}/lib/security
%dir %{jvmjardir}
%dir %{syslibdir}/gcj
%{_bindir}/rebuild-gcj-db
%{_jvmdir}/%{jredir}/bin/java
%{_jvmdir}/%{jredir}/bin/keytool
%{_jvmdir}/%{jredir}/bin/rmiregistry
%{_jvmdir}/%{jredir}/lib/security/cacerts
%{_jvmdir}/%{jredir}/lib/security/java.security
%{_jvmdir}/%{jredir}/lib/jaas.jar
%{_jvmdir}/%{jredir}/lib/jce.jar
%{_jvmdir}/%{jredir}/lib/jdbc-stdext.jar
%{_jvmdir}/%{jredir}/lib/jndi-cos.jar
%{_jvmdir}/%{jredir}/lib/jndi-dns.jar
%{_jvmdir}/%{jredir}/lib/jndi-ldap.jar
%{_jvmdir}/%{jredir}/lib/jndi-rmi.jar
%{_jvmdir}/%{jredir}/lib/jndi.jar
%{_jvmdir}/%{jredir}/lib/jsse.jar
%{_jvmdir}/%{jredir}/lib/sasl.jar
%ifarch x86_64
%{_jvmdir}/%{jredir}/lib/amd64
%endif
%{_jvmdir}/%{jrelnk}
%{jvmjardir}/jaas.jar
%{jvmjardir}/jaas-%{javaver}.jar
%{jvmjardir}/jaas-%{version}.jar
%{jvmjardir}/jce.jar
%{jvmjardir}/jce-%{javaver}.jar
%{jvmjardir}/jce-%{version}.jar
%{jvmjardir}/jdbc-stdext.jar
%{jvmjardir}/jdbc-stdext-%{javaver}.jar
%{jvmjardir}/jdbc-stdext-%{version}.jar
%{jvmjardir}/jndi.jar
%{jvmjardir}/jndi-%{javaver}.jar
%{jvmjardir}/jndi-%{version}.jar
%{jvmjardir}/jndi-cos.jar
%{jvmjardir}/jndi-cos-%{javaver}.jar
%{jvmjardir}/jndi-cos-%{version}.jar
%{jvmjardir}/jndi-dns.jar
%{jvmjardir}/jndi-dns-%{javaver}.jar
%{jvmjardir}/jndi-dns-%{version}.jar
%{jvmjardir}/jndi-ldap.jar
%{jvmjardir}/jndi-ldap-%{javaver}.jar
%{jvmjardir}/jndi-ldap-%{version}.jar
%{jvmjardir}/jndi-rmi.jar
%{jvmjardir}/jndi-rmi-%{javaver}.jar
%{jvmjardir}/jndi-rmi-%{version}.jar
%{jvmjardir}/jsse.jar
%{jvmjardir}/jsse-%{javaver}.jar
%{jvmjardir}/jsse-%{version}.jar
%{jvmjardir}/sasl.jar
%{jvmjardir}/sasl-%{javaver}.jar
%{jvmjardir}/sasl-%{version}.jar
%{_jvmjardir}/%{jrelnk}
%ghost %{_jvmdir}/%{sdkdir}/jre/lib/rt.jar
%ghost %{_jvmdir}/%{jredir}/lib/%{_arch}/libjawt.so
%ghost %{_jvmdir}/%{jredir}/lib/%{_arch}/client/libjvm.so
%ghost %{_jvmdir}/%{jredir}/lib/%{_arch}/server/libjvm.so
# These must not be marked %config(noreplace).  Their file names are
# used in post and postun.  Their contents are ignored, so replacing
# them doesn't matter.  .rpmnew files are harmful since they're
# interpreted by post and postun as classnames ending in rpmnew.
%{_sysconfdir}/java/security/security.d/1000-gnu.java.security.provider.Gnu
%{_sysconfdir}/java/security/security.d/1001-gnu.javax.crypto.jce.GnuCrypto
%{_sysconfdir}/java/security/security.d/1002-gnu.javax.crypto.jce.GnuSasl
%{_sysconfdir}/java/security/security.d/1003-gnu.javax.net.ssl.provider.Jessie
%{_sysconfdir}/java/security/security.d/1004-gnu.javax.security.auth.callback.GnuCallbacks

%files devel
%defattr(-,root,root,-)
%dir %{_jvmdir}/%{sdkdir}/bin
%dir %{_jvmdir}/%{sdkdir}/include
%dir %{_jvmdir}/%{sdkdir}/include/linux
%dir %{_jvmdir}/%{sdkdir}/lib
%{_bindir}/aot-compile
%{_bindir}/aot-compile-rpm
%{python_sitelib}/aotcompile.py*
%{python_sitelib}/classfile.py*
%{python_sitelib}/java_gcj_compat-%{jgcver}-py?.?.egg-info
%{_jvmdir}/%{sdkdir}/bin/appletviewer
%{_jvmdir}/%{sdkdir}/bin/jar
%{_jvmdir}/%{sdkdir}/bin/jarsigner
%{_jvmdir}/%{sdkdir}/bin/java
%{_jvmdir}/%{sdkdir}/bin/javac
%{_jvmdir}/%{sdkdir}/bin/javadoc
%{_jvmdir}/%{sdkdir}/bin/javah
%{_jvmdir}/%{sdkdir}/bin/keytool
%{_jvmdir}/%{sdkdir}/bin/rmic
%{_jvmdir}/%{sdkdir}/bin/rmiregistry
%{_jvmdir}/%{sdklnk}
%{_jvmjardir}/%{sdklnk}
%ghost %{_jvmdir}/%{sdkdir}/include/jawt.h
%ghost %{_jvmdir}/%{sdkdir}/include/jni.h
%ghost %{_jvmdir}/%{sdkdir}/include/linux/jawt_md.h
%ghost %{_jvmdir}/%{sdkdir}/include/linux/jni_md.h
%ghost %{_jvmdir}/%{sdkdir}/lib/tools.jar

%files src
%defattr(-,root,root,-)
%ghost %{_jvmdir}/%{sdkdir}/src.zip

%if ! %{bootstrap}
%files javadoc
%defattr(-,root,root,-)
%doc %{_javadocdir}/%{name}
# A JPackage that "provides" this directory will, in its %post script,
# remove the existing directory and install a new symbolic link to its
# versioned directory.  For Fedora we want clear file ownership so we
# make java-1.5.0-gcj-javadoc own this file.  Installing the
# corresponding JPackage over java-1.5.0-gcj-javadoc will work but
# will invalidate this file.
%doc %{_javadocdir}/java
%endif

%if %{enable_plugin}
%files plugin
%defattr(-,root,root,-)
%endif

%changelog
* Mon Nov 30 2009 Dennis Gregorovic <dgregor@redhat.com> - 1.5.0.0-29.1
- Rebuilt for RHEL 6

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.0.0-29
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue May 12 2009 Stepan Kasal <skasal@redhat.com> 1.5.0.0-28
- another attempt to rebuild, adding a workaround for #500314

* Fri Apr 03 2009 Karsten Hopp <karsten@redhat.com> 1.5.0.0-27
- update workaround patch to fix rebuild problems

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.0.0-26
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Dec 17 2008 Lillian Angel <langel@redhat.com> - 1.5.0.0-25
- Updated jgcver to 1.0.79.
- Updated release.

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 1.5.0.0-24
- Fix locations for Python 2.6

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 1.5.0.0-23
- Rebuild for Python 2.6

* Tue Aug  5 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 1.5.0.0-22
- fix license tag

* Thu Apr  3 2008 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.5.0.0-21
- Import java-gcj-compat 1.0.78.
- Resolves: rhbz#283831

* Thu Apr  3 2008 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.5.0.0-21
- Re-add python egg-info file.

* Thu Apr  3 2008 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.5.0.0-21
- Require java-1.6.0-openjdk-devel for javadoc instead of sinjdoc.

* Wed Apr  2 2008 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.5.0.0-21
- Commit patch to add proper triggerin requires from Orion Poplawski
  <orion@cora.nwra.com>.
- Resolves: rhbz#436838

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1.5.0.0-20
- Autorebuild for GCC 4.3

* Mon Jan 21 2008 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.5.0.0-19
- Include python egg-info file.
- Work around rhbz#404981
- Inline rebuild-security-providers.
- Resolves: rhbz#260161

* Tue Nov 27 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.5.0.0-18
- Import java-gcj-compat 1.0.77.

* Wed Oct 17 2007 Tom "spot" Callaway <tcallawa@redhat.com> - 1.5.0.0-17
- fix aot-compile-rpm to not run inside the buildroot

* Tue Oct 16 2007 Dennis Gilmore <dennis@ausil.us> - 1.5.0.0-16
- add sparc64 to the list of 64 bit archs

* Tue May 15 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.5.0.0-15
- Require findutils for post and postun.
- Resolves: rhbz#240159

* Mon Apr 16 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.5.0.0-14
- Import java-gcj-compat 1.0.76.
- Related: rhbz#200836

* Tue Apr 10 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.5.0.0-13
- Import java-gcj-compat 1.0.75.
- Point URL field at java-gcj-compat home page.
- Require openssl for build.
- Generate and include cacerts.
- Resolves: rhbz#200836 rhbz#233239

* Tue Apr  3 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.5.0.0-12
- Obsolete gnu-crypto, gnu-crypto-sasl-jdk1.4 and jessie in base
  package.
- Obsolete gnu-crypto-javadoc in javadoc subpackage.

* Mon Mar 26 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.5.0.0-11
- Disable bootstrap mode.

* Mon Mar 26 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.5.0.0-10
- Import java-gcj-compat 1.0.74.

* Mon Mar 26 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.5.0.0-9
- Re-add gcj-java build requirement.

* Mon Mar 26 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.5.0.0-8
- Make -devel subpackage require libgcj-src.

* Sat Mar 24 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.5.0.0-7
- Import java-gcj-compat 1.0.73.
- Remove java-1.4.2-gcj-compat compatibility symlinks.
- Install tools.jar symlink to libgcj-tools.jar.
- Remove gcc-java and eclipse-ecj build requirements.
- Remove workaround for ppc64 file system corruption.
- Remove workaround for gjdoc/libgcj rounding error.

* Mon Mar 19 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.5.0.0-6
- Set bootstrap to 0.
- Remove bootstrap hacks.

* Mon Mar 19 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.5.0.0-5
- Remove broken multilib support.
- Set bootstrap to 1.
- Add JAVA_HOME bootstrap hack.
- Add java-1.4.2-gcj-compat-devel bootstrap hack.
- Add bootstrap ecj script.
- Remove JAVA_HOME and java-1.4.2-gcj-compat-devel bootstrap hacks.
- Another bootstrap attempt.

* Fri Mar 16 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.5.0.0-4
- Remove config(noreplace) markings on security.d files.
- Make java-1.4.2-gcj-compat* provides strictly-greater-than
  1.4.2.0-40jpp.111.
- Remove gjdoc build requirement.
- Import java-gcj-compat 1.0.72.

* Fri Mar 16 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.5.0.0-3
- Require sinjdoc.

* Thu Mar 15 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.5.0.0-2
- Set bootstrap to 0 to build javadoc sub-package, now that sinjdoc
  has been built.
- Add temporary gjdoc build requirement.

* Thu Mar 15 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 1.5.0.0-1
- Set bootstrap to 1 since sinjdoc is not yet available to build
  javadocs.
- Import java-gcj-compat 1.0.70.
- Port java-1.4.2-gcj-compat to java-1.5.0-gcj.

* Thu Dec  7 2006 Jeremy Katz <katzj@redhat.com> - 0:1.4.2.0-40jpp.111
- rebuild for python 2.5

* Tue Oct 10 2006 Thomas Fitzsimmons <fitzsim@redhat.com>
- Require gij binary explicitly. (208913)

* Wed Sep 13 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp.109
- Require gcj-dbtool for post and postun. (205103)

* Thu Sep  7 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp.108
- Move Double.html manipulation within ppc64 filesystem check.
- Import java-gcj-compat 1.0.68 to eliminate rebuild-gcj-db multilib
  conflict.
- Work around gjdoc/libgcj rounding error in Double.html.

* Thu Sep  7 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp.107
- Give aotcompile.py a consistent timestamp. (205216)

* Wed Sep  6 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp.106
- Bump release number.

* Thu Aug 31 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp.105
- Comment out and obsolete plugin subpackage. (204728)
- Import java-gcj-compat 1.0.65.

* Wed Aug 30 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp.104
- Import java-gcj-compat 1.0.64.

* Tue Aug 29 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp.103
- Import java-gcj-compat 1.0.63.

* Wed Aug 23 2006 Fernando Nasser <fnasser@redhat.com> - 0:1.4.2.0-40jpp.102
- Remove duplicate macro definitions
- Rebuild

* Mon Aug 14 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_101rh
- Add libgcj-devel to devel and src post and postun
  requirements. (202007)
- Require libgcj in plugin package. (202268)

* Fri Aug  4 2006 Gary Benson <gbenson@redhat.com>
- Move aot-compile and its libraries to the devel subpackage.

* Tue Aug  1 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_100rh
- Require gcc-java for devel and src post and postun. (199942)
- Require libgcj for plugin post and postun. (199942)

* Mon Jul 31 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_99rh
- Add new built-in security providers.

* Mon Jul 24 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_98rh
- Import java-gcj-compat 1.0.61.

* Sun Jul 23 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_97rh
- Link jsse.jar to libgcj.jar.

* Sat Jul 22 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_96rh
- Remove gjdoc workaround.

* Sat Jul 22 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_95rh
- Remove hack-libgcj requirement.
- Work around gjdoc failure by not building javadocs.

* Fri Jul 21 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_95rh
- Require hack-libgcj for build. (dist-fc6-java)

* Fri Jul 21 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_94rh
- Add plugin subpackage.
- Install libjawt.so and libjvm.so symlinks.
- Install appletviewer, jarsigner and keytool symlinks.
- Import java-gcj-compat 1.0.60.

* Fri Jul 21 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_93rh
- Import java-gcj-compat 1.0.59.
- Use standard BuildRoot tag.
- Remove gnu-crypto and jessie requires.
- Remove static compile method patch.

* Mon Jul 17 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_89rh
- Remove BouncyCastle.

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 0:1.4.2.0-40jpp_88rh
- rebuild

* Tue Jun 20 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_87rh
- Make com.sun.tools.javac.Main.compile method static.

* Mon Jun 19 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_86rh
- Provide jdbc-stdext.

* Wed Jun 14 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_85rh
- Require zip.

* Mon Jun 12 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_84rh
- Remove bootstrap logic.
- Fix ppc64 file system corruption workaround.
- Make ecj.sh.in call gij.
- Require eclipse-ecj to build.

* Fri Mar  3 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_83rh
- Make javadoc post scriplet pass unconditionally.
- Force symlinks in javadoc post scriptlet.

* Wed Mar  1 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_82rh
- Add chkconfig as a prerequisite.

* Wed Mar  1 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_81rh
- Natively compile BouncyCastle.
- Move bcprov in the build section so that it is found by bootstrap
  architectures in the install section.
- Only include BC library directory on non-boostrap architectures.

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 0:1.4.2.0-40jpp_80rh
- bump again for double-long bug on ppc(64)

* Fri Feb 10 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_79rh
- Install compatibility amd64 symlink.

* Wed Feb  8 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_78rh
- Install javadocs in versioned directory.

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 0:1.4.2.0-40jpp_77rh
- rebuilt for new gcc4.1 snapshot and glibc changes

* Mon Feb  6 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_76rh
- Test src.zip before extracting its contents.

* Mon Feb  6 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_75rh
- Use fastjar to extract libgcj sources instead of unzip.

* Mon Feb  6 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_74rh
- Require gjdoc and libgcj-src packages for build.
- Build API documentation.
- Add -javadoc package.

* Thu Feb  2 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_73rh
- Adjust Jessie and GNU Crypto version requirements.
- Uncomment ifnarch ia64 sections.

* Thu Feb  2 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_71rh
- Obsolete gnu-crypto-sasl-jdk1.4 and gnu-crypto-jce-jdk1.4 regardless of versions.

* Thu Feb  2 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_70rh
- Remove all ifnarch ia64 sections.

* Thu Feb  2 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_69rh
- Don't call aot-compile-rpm on bootstrap architectures.

* Thu Feb  2 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_68rh
- Obsolete gnu-crypto-sasl-jdk1.4 and gnu-crypto-jce-jdk1.4.
- Provide java-sasl and jce.

* Thu Feb  2 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_67rh
- Remove conditional BuildRequires, which isn't supported by beehive.

* Thu Feb  2 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_66rh
- Fix ecj script location when building BouncyCastle in bootstrap mode.
- Do not BuildRequires eclipse-ecj in bootstrap mode.
- Build BouncyCastle with bootstrap ecj script in bootstrap mode.

* Fri Jan 27 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_64rh
- Import BouncyCastle 1.3.1.
- Re-enable BouncyCastle provider.

* Wed Jan 25 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_63rh
- Import java-gcj-compat 1.0.52.

* Mon Jan 16 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_62rh
- Remove aot-compile-rpm and rebuild-gcj-db when building a custom RPM.
- Import java-gcj-compat 1.0.51.

* Mon Jan  9 2006 Archit Shah <ashah@redhat.com> - 0:1.4.2.0-40jpp_61rh
- Import java-gcj-compat 1.0.50.

* Fri Jan  6 2006 Archit Shah <ashah@redhat.com> - 0:1.4.2.0-40jpp_60rh
- Import java-gcj-compat 1.0.48.

* Wed Jan  4 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_59rh
- Import java-gcj-compat 1.0.47.

* Wed Jan  4 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_58rh
- Import java-gcj-compat 1.0.46.

* Wed Dec 21 2005 Jesse Keating <jkeating@redhat.com> - 0:1.4.2.0-40jpp_57rh
- rebuilt again w/ another new gcc

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Wed Nov 30 2005 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_56rh
- Bump release number.

* Wed Nov 16 2005 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_55rh
- Call rebuild-security-providers conditionally on its existence.

* Tue Nov 15 2005 Archit Shah <ashah@redhat.com> 0:1.4.2.0-40jpp_54rh
- Import java-gcj-compat 1.0.45.

* Mon Nov 14 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-40jpp_53rh
- Bump release number.

* Mon Nov 14 2005 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_52rh
- Import java-gcj-compat 1.0.44.
- Make aot-compile-rpm and rebuild-gcj-db real scripts, not
  alternatives symlinks.
- Put rebuild-gcj-db in base package.

* Wed Sep 21 2005 Gary Benson <gbenson@redhat.com>  - 0:1.4.2.0-40jpp_51rh
- Import java-gcj-compat 1.0.43.

* Tue Sep 20 2005 Gary Benson <gbenson@redhat.com>  - 0:1.4.2.0-40jpp_50rh
- Import java-gcj-compat 1.0.42.

* Tue Sep  6 2005 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_49rh
- Import java-gcj-compat 1.0.41.

* Tue Sep  6 2005 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_48rh
- Don't include security provider file in custom builds.
- Don't mark security provider file as config(noreplace).

* Wed Aug 31 2005 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_47rh
- Import java-gcj-compat 1.0.40.
- Point jaxp_parser_impl at proper libgcj-<version>.jar for custom
  builds.

* Wed Aug 31 2005 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_46rh
- Don't autogenerate libjawt.so dependencies in custom builds.

* Tue Aug 30 2005 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_45rh
- Import java-gcj-compat 1.0.39.
- Remove libjawt.so symlinks.
- Symlink to jni_md.h.

* Tue Aug 30 2005 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_44rh
- Install ecj when building a custom java-1.4.2-gcj-compat.
- Fix removal of jaxp_parser_impl.jar alternative.

* Mon Aug 29 2005 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.4.2.0-40jpp_44rh
- Import java-gcj-compat 1.0.37.
- Remove aot-compile and find-and-aot-compile.
- Make aot-compile-rpm and rebuild-gcj-db alternatives symlinks.
- Mark security file config(noreplace).

* Thu Jul 28 2005 Gary Benson <gbenson@redhat.com> 0:1.4.2.0-40jpp_43rh
- Upgrade bootstrap ecj to pick up classpath parser fix.
- Import java-gcj-compat 1.0.36.

* Fri Jul 22 2005 Gary Benson <gbenson@redhat.com> 0:1.4.2.0-40jpp_42rh
- Remove jta compatibility stuff.

* Thu Jul 21 2005 Gary Benson <gbenson@redhat.com> 0:1.4.2.0-40jpp_41rh
- Remove servletapi and jspapi now that tomcat5 is built.

* Wed Jul 20 2005 Gary Benson <gbenson@redhat.com> 0:1.4.2.0-40jpp_40rh
- Import java-gcj-compat 1.0.35.

* Tue Jul 19 2005 Gary Benson <gbenson@redhat.com> 0:1.4.2.0-40jpp_39rh
- Import java-gcj-compat 1.0.34.
- Provide servletapi and jspapi for bootstrapping.

* Thu Jul 14 2005 Gary Benson <gbenson@redhat.com> 0:1.4.2.0-40jpp_38rh
- Import java-gcj-compat 1.0.33.

* Wed Jul 13 2005 Gary Benson <gbenson@redhat.com> 0:1.4.2.0-40jpp_37rh
- Add virtual dependencies to indicate our upstream version.
- Import java-gcj-compat 1.0.32.

* Fri Jul  8 2005 Gary Benson <gbenson@redhat.com> 0:1.4.2.0-40jpp_36rh
- Replace the binary ecj with a script to work around #162748.

* Thu Jul  7 2005 Gary Benson <gbenson@redhat.com> 0:1.4.2.0-40jpp_33rh
- Bootstrap onto ia64, ppc64, s390 and s390x.
- Add python dependency for aot-compile-rpm.

* Thu Jul  7 2005 Gary Benson <gbenson@redhat.com> 0:1.4.2.0-40jpp_32rh
- Import java-gcj-compat 1.0.31.
- Move the aot-compile scripts to the devel subpackage.

* Mon Jun  6 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-40jpp_31rh
- Add jaxp_parser_impl.jar alternative. (#158751)
- Separate post and postun requires lines.
- Use gij, not gcj to compute version strings in post and triggerin sections.

* Thu May 26 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-40jpp_30rh
- Add jaxp_parser_impl.jar alternative. (#158751)

* Thu May 26 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-40jpp_29rh
- Separate post and postun requires lines

* Thu May 26 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-40jpp_28rh
- Re-remove bouncy castle provider.

* Thu May 26 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-40jpp_27rh
- Re-add bouncy castle provider. (#146782)

* Wed May 25 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-40jpp_26rh
- Import java-gcj-compat 1.0.30.

* Wed May 25 2005 Gary Benson <gbenson@redhat.com> 0:1.4.2.0-40jpp_25rh
- Update tools.jar with the ecj's new jarfile name (#158734).

* Fri May 20 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-40jpp_24rh
- Update libjawt.so symlink to reflect libgcjawt.so's new name.

* Thu May 19 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-40jpp_23rh
- Import java-gcj-compat 1.0.29.

* Wed May 18 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-40jpp_22rh
- Move gcc-java requirement from base to -devel.

* Wed May 18 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-40jpp_21rh
- Comment out bouncy castle stuff.

* Tue May 17 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-40jpp_20rh
- Require jpackage-utils for post and postun.
- Run rebuild-security-providers with full path.

* Tue May 17 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-40jpp_19rh
- Require eclipse-ecj for build.
- Include Bouncy Castle provider.
- Exclusive arch ix86, x86_64 and ppc.

* Wed May 11 2005 Andrew Overholt <overholt@redhat.com>
- Add machinery to allow for use with non-system gcc installations.

* Fri Apr 15 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-40jpp_18rh
- Require gnu-crypto.

* Fri Apr 15 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-40jpp_17rh
- Provide jaxp_parser_impl.

* Wed Apr 13 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-40jpp_16rh
- Import java-gcj-compat 1.0.28.

* Mon Apr  4 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-40jpp_15rh
- Import java-gcj-compat 1.0.27.
- Bump gccver to 4.0.0-0.39.
- Make -devel take ownership of symlinks as well as regular files.

* Wed Mar 30 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-40jpp_14rh
- Import java-gcj-compat 1.0.23.
- Always look for classpath.security in /usr/lib. (151561)
- Provide jsse. (151662)

* Thu Mar 17 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-40jpp_13rh
- Uncomment rebuild-security-providers.
- Require jessie >= 1.0.0-3.

* Tue Mar 15 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-40jpp_12rh
- Don't re-run rebuild-security-providers.

* Tue Mar 15 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-40jpp_11rh
- Add jaas and jta provides.

* Tue Mar  8 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-40jpp_10rh
- Import java-gcj-compat 1.0.22.
- Symlink jaas.jar, jdbc-stdext.jar, jndi.jar and jta.jar to
  libgcj.jar.

* Sat Mar  5 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-40jpp_9rh
- Import java-gcj-compat 1.0.21.

* Sat Mar  5 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-40jpp_8rh
- Import java-gcj-compat 1.0.20.
- Depend on jessie.
- Install jsse.jar.
- Install security directory.
- Symlink classpath.security to java.security.

* Sat Mar  5 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-40jpp_7rh
- Import java-gcj-compat 1.0.19.

* Thu Mar  3 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-40jpp_6rh
- Import java-gcj-compat 1.0.18.

* Thu Mar  3 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-40jpp_5rh
- Update descriptions.

* Wed Mar  2 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-40jpp_4rh
- Bump release number.

* Wed Mar  2 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-40jpp_3rh
- Make java-1.4.2-gcj-compat-devel obsolete java-1.4.2-gcj4-compat-devel.
- Import java-gcj-compat 1.0.17.
- Specify --with-arch-directory and --with-os-directory options on
  configure line.

* Tue Mar  1 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-40jpp_2rh
- Make arch-specific.

* Tue Mar  1 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-40jpp_1rh
- Merge java-1.4.2-gcj4-compat into java-1.4.2-gcj-compat.
- Import java-gcj-compat 1.0.15.
- Add AWT Native Interface symlinks.
- Remove build requires on eclipse-ecj.

* Thu Feb 17 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-4jpp_4rh
- Add -src sub-package.

* Wed Feb  9 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-4jpp_3rh
- Import java-gcj-compat 1.0.14.

* Tue Feb  8 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-4jpp_2rh
- Import java-gcj-compat 1.0.13.

* Mon Feb  7 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-4jpp_1rh
- Import java-gcj-compat 1.0.12.

* Wed Feb  2 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-4jpp_1rh
- Add Red Hat release number.

* Tue Feb  1 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-4jpp
- Remove gjdoc version requirement.
- Change java-gcj-compat version number.

* Tue Feb  1 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-4jpp
- Import java-gcj-compat 1.0.11.
- Require gjdoc.

* Tue Feb  1 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-4jpp
- Add jni.h symlink.
- Install rt.jar as an unmanaged symlink.
- Conflict and obsolete old java-gcj-compat rpms.
- Import java-gcj-compat 1.0.9.

* Mon Jan 24 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-3jpp
- Import java-gcj-compat 1.0.8.

* Thu Jan 13 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-2jpp
- Make jvmjardir use cname, not name.

* Wed Jan 12 2005 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.4.2.0-1jpp
- Initial build.
