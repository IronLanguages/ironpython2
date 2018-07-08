# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the Apache 2.0 License.
# See the LICENSE file in the project root for more information.


# -----------------------------------------------------------------------------
# -- Initial Setup

if ($env:DLR_ROOT -eq $null) {
	echo "DLR_ROOT is not set.  Cannot continue!"
	exit 1
}

. "$env:DLR_ROOT\Test\Scripts\install_dlrcom.ps1"
if (! $?) {
	echo "Failed to source and run "$env:DLR_ROOT\Test\Scripts\install_dlrcom.ps1".  Cannot continue!"
	exit 1
}

if ("$env:DLR_BIN" -eq "") {
	log-critical "DLR_BIN is not set.  Cannot continue!"
}

if (! (test-path $env:DLR_BIN\ipy.exe)) {
	log-critical "$env:DLR_BIN\ipy.exe does not exist.  Cannot continue!"
}
set-alias rowipy $env:DLR_ROOT\Languages\IronPython\Internal\ipy.bat



# ------------------------------------------------------------------------------
# -- Run the test

pushd $env:DLR_ROOT\Languages\IronPython\Tests

log-info "Running the following COM test: $PWD> $env:DLR_BIN\ipy.exe $args"
rowipy $args[0].Split(" ")
$EC = $LASTEXITCODE

popd
exit $EC
