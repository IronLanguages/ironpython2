#!/bin/sh
BASEDIR=$(dirname $0)
ABS_PATH=`cd "$BASEDIR"; pwd`
dotnet --additional-deps "$ABS_PATH/Mono.Posix.NETStandard.deps.json" "$ABS_PATH/ipy.dll" $@