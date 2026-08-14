################################################################################
#
# qt5webkit
#
################################################################################

QT5WEBKIT_VERSION = 5.212.0-alpha4
QT5WEBKIT_SITE = https://github.com/qtwebkit/qtwebkit/releases/download/qtwebkit-$(QT5WEBKIT_VERSION)
QT5WEBKIT_SOURCE = qtwebkit-$(QT5WEBKIT_VERSION).tar.xz
QT5WEBKIT_DEPENDENCIES = \
	host-bison host-flex host-gperf host-python3 host-ruby gstreamer1 \
	gst1-plugins-base icu leveldb jpeg libpng libxml2 libxslt qt5location \
	openssl qt5sensors qt5webchannel sqlite webp woff2
QT5WEBKIT_INSTALL_STAGING = YES

QT5WEBKIT_LICENSE_FILES = Source/WebCore/LICENSE-LGPL-2 Source/WebCore/LICENSE-LGPL-2.1

QT5WEBKIT_LICENSE = LGPL-2.1+, BSD-3-Clause, BSD-2-Clause
# Source files contain references to LGPL_EXCEPTION.txt but it is not included
# in the archive.
QT5WEBKIT_LICENSE_FILES += LICENSE.LGPLv21

ifeq ($(BR2_MIPS_CPU_MIPS32R6),y)
QT5WEBKIT_CONF_OPTS += -DENABLE_JIT=OFF
endif

ifeq ($(BR2_PACKAGE_QT5BASE_OPENGL),y)
QT5WEBKIT_CONF_OPTS += \
	-DENABLE_OPENGL=ON \
	-DENABLE_WEBKIT2=ON
else
QT5WEBKIT_CONF_OPTS += \
	-DENABLE_OPENGL=OFF \
	-DENABLE_WEBKIT2=OFF
endif

ifeq ($(BR2_PACKAGE_QT5BASE_XCB),y)
QT5WEBKIT_DEPENDENCIES += xlib_libXcomposite xlib_libXext xlib_libXrender
endif

ifeq ($(BR2_PACKAGE_QT5DECLARATIVE),y)
QT5WEBKIT_DEPENDENCIES += qt5declarative
endif

ifeq ($(BR2_PACKAGE_LIBEXECINFO),y)
QT5WEBKIT_DEPENDENCIES += libexecinfo
endif

ifeq ($(BR2_TOOLCHAIN_USES_MUSL),y)
QT5WEBKIT_CONF_OPTS += -DENABLE_SAMPLING_PROFILER=OFF
endif

QT5WEBKIT_CONF_OPTS += \
	-DENABLE_TOOLS=OFF \
	-DPORT=Qt \
	-DPYTHON_EXECUTABLE=$(HOST_DIR)/bin/python3 \
	-DSHARED_CORE=ON \
	-DUSE_LIBHYPHEN=OFF

# qmake looks for module metadata below QT_HOST_DATA. QtWebKit's CMake
# install instead places these files below the target prefix.
define QT5WEBKIT_INSTALL_QMAKE_MODULES
	$(INSTALL) -m 0644 \
		$(STAGING_DIR)/usr/mkspecs/modules/qt_lib_webkit*.pri \
		$(HOST_DIR)/mkspecs/modules/
	$(SED) 's#^QT\.webkit\.includes =.*#QT.webkit.includes = $$$$[QT_INSTALL_PREFIX]/include $$$$[QT_INSTALL_PREFIX]/include/QtWebKit#' \
		$(HOST_DIR)/mkspecs/modules/qt_lib_webkit.pri
	$(SED) 's#^QT\.webkit_private\.includes =.*#QT.webkit_private.includes = $$$$[QT_INSTALL_PREFIX]/include/QtWebKit/$(QT5WEBKIT_VERSION) $$$$[QT_INSTALL_PREFIX]/include/QtWebKit/$(QT5WEBKIT_VERSION)/QtWebKit#' \
		$(HOST_DIR)/mkspecs/modules/qt_lib_webkit_private.pri
	$(SED) 's#^QT\.webkitwidgets\.includes =.*#QT.webkitwidgets.includes = $$$$[QT_INSTALL_PREFIX]/include $$$$[QT_INSTALL_PREFIX]/include/QtWebKitWidgets#' \
		$(HOST_DIR)/mkspecs/modules/qt_lib_webkitwidgets.pri
	$(SED) 's#^QT\.webkitwidgets_private\.includes =.*#QT.webkitwidgets_private.includes = $$$$[QT_INSTALL_PREFIX]/include/QtWebKitWidgets/$(QT5WEBKIT_VERSION) $$$$[QT_INSTALL_PREFIX]/include/QtWebKitWidgets/$(QT5WEBKIT_VERSION)/QtWebKitWidgets#' \
		$(HOST_DIR)/mkspecs/modules/qt_lib_webkitwidgets_private.pri
	$(SED) 's#\.libs =.*#\.libs = $$$$QT_MODULE_LIB_BASE#' \
		$(HOST_DIR)/mkspecs/modules/qt_lib_webkit*.pri
endef
QT5WEBKIT_POST_INSTALL_STAGING_HOOKS += QT5WEBKIT_INSTALL_QMAKE_MODULES

$(eval $(cmake-package))
