#!/usr/bin/env fish

# ------------------------------------------------------------
# analyze_binary.fish
#
# Usage:
#
#   ./analyze_binary.fish BrewieApplication
#
# ------------------------------------------------------------

if test (count $argv) -lt 1
    echo "Usage: $argv[1] <ELF>"
    exit 1
end

# ------------------------------------------------------------
# Toolchain
# ------------------------------------------------------------

source fish_env

set ELF $argv[1]
set REPORT reports

mkdir -p $REPORT

echo "Analyzing $ELF"
echo

# ------------------------------------------------------------
# 00 Summary
# ------------------------------------------------------------

echo "# ELF Analysis Summary" > $REPORT/00-summary.md
echo "" >> $REPORT/00-summary.md
date >> $REPORT/00-summary.md
echo "" >> $REPORT/00-summary.md

# ------------------------------------------------------------
# ELF Header
# ------------------------------------------------------------

$TOOLPREFIX-readelf -h $ELF \
> $REPORT/01-header.txt

# ------------------------------------------------------------
# Program Headers
# ------------------------------------------------------------

$TOOLPREFIX-readelf -l $ELF \
> $REPORT/02-program-headers.txt

# ------------------------------------------------------------
# Sections
# ------------------------------------------------------------

$TOOLPREFIX-readelf -S $ELF \
> $REPORT/03-sections.txt

# ------------------------------------------------------------
# Symbols
# ------------------------------------------------------------

$TOOLPREFIX-nm \
    -C \
    -n \
    $ELF \
> $REPORT/04-symbols.txt

# ------------------------------------------------------------
# Dynamic Section
# ------------------------------------------------------------

$TOOLPREFIX-readelf \
    -d \
    $ELF \
> $REPORT/05-dynamic.txt

# ------------------------------------------------------------
# Needed Libraries
# ------------------------------------------------------------

$TOOLPREFIX-readelf \
    -d \
    $ELF \
| grep NEEDED \
> $REPORT/06-needed-libraries.txt

# ------------------------------------------------------------
# Debug Information
# ------------------------------------------------------------

$TOOLPREFIX-readelf \
    --debug-dump=info \
    $ELF \
> $REPORT/07-debug-info.txt

# ------------------------------------------------------------
# Source Files
# ------------------------------------------------------------

$TOOLPREFIX-readelf \
    -wi \
    $ELF \
| grep DW_AT_name \
> $REPORT/08-source-files.txt

# ------------------------------------------------------------
# Qt Analysis
# ------------------------------------------------------------

$TOOLPREFIX-strings $ELF \
| grep -Ei 'Qt|QObject|QMainWindow|QWidget|QDialog|QThread|QSerialPort|QSql|QNetwork|QApplication' \
| sort -u \
> $REPORT/09-qt-analysis.txt

# ------------------------------------------------------------
# Strings
# ------------------------------------------------------------

$TOOLPREFIX-strings \
    -a \
    $ELF \
> $REPORT/10-strings.txt

# ------------------------------------------------------------
# Network
# ------------------------------------------------------------

grep -Ei \
'http|https|tcp|udp|socket|ssl|tls|ftp|wifi|wlan|dhcp|dns|mqtt|cloud|update' \
$REPORT/10-strings.txt \
> $REPORT/11-network.txt

# ------------------------------------------------------------
# Serial
# ------------------------------------------------------------

grep -Ei \
'tty|ttyS|ttyUSB|ttyAMA|serial|uart|rs232|rs485|modbus' \
$REPORT/10-strings.txt \
> $REPORT/12-serial.txt

# ------------------------------------------------------------
# Resources
# ------------------------------------------------------------

grep -Ei \
'\.png|\.jpg|\.svg|\.ui|\.qrc|\.qm|\.gif|\.bmp|\.ttf|\.sqlite|\.db' \
$REPORT/10-strings.txt \
> $REPORT/13-resources.txt

# ------------------------------------------------------------
# JSON Summary
# ------------------------------------------------------------

printf '{\n' > $REPORT/14-summary.json
printf '  "file": "%s"\n' $ELF >> $REPORT/14-summary.json
printf '}\n' >> $REPORT/14-summary.json

# ------------------------------------------------------------
# Update summary
# ------------------------------------------------------------

echo "" >> $REPORT/00-summary.md
echo "Generated Reports" >> $REPORT/00-summary.md
echo "-----------------" >> $REPORT/00-summary.md

for f in $REPORT/*
    echo (basename $f) >> $REPORT/00-summary.md
end

echo
echo "Done."
echo
ls -lh $REPORT
