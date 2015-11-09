TEMPLATE = lib
TARGET = qscilexerrest
SOURCES = scilexerrest.cpp
HEADERS = scilexerrest.h

QT += widgets printsupport

CONFIG += static release qscintilla2

DEFINES += QSCINTILLA_DLL

INCLUDEPATH += $$[QT_INSTALL_HEADERS]

LIBS += -L$$[QT_INSTALL_LIBS]
