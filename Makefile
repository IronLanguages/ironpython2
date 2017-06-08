.PHONY: debug release test stage package clean test-smoke test-smoke-debug test-ironpython test-ironpython-debug test-cpython test-cpython-debug test-all test-all-debug

release:
	@xbuild Build.proj /t:Build /p:Mono=true /p:BuildFlavour=Release /p:Platform="Any CPU" /verbosity:minimal /nologo
	cp Src/DLR/bin/Release/rowantest.*.dll bin/Release/
	cp Src/DLR/bin/v4Release/rowantest.*.dll bin/v4Release/

debug:
	@xbuild Build.proj /t:Build /p:Mono=true /p:BuildFlavour=Debug /p:Platform="Any CPU" /verbosity:minimal /nologo
	cp Src/DLR/bin/Debug/rowantest.*.dll bin/Debug/
	cp Src/DLR/bin/v4Debug/rowantest.*.dll bin/v4Debug/

stage:
	@xbuild Build.proj /t:Stage /p:Mono=true /p:BuildFlavour=Release /verbosity:minimal /nologo

package:
	@xbuild Build.proj /t:Package /p:Mono=true /p:BuildFlavour=Release /verbosity:minimal /nologo

clean:
	@xbuild Build.proj /t:Clean /p:Mono=true /verbosity:minimal /nologo

test-ironpython:
	(cd bin/Release && mono ./IronPythonTest.exe --labels=All --where:Category==IronPython --result:ironpython-net45-release-result.xml) || true
	(cd bin/v4Release && mono ./IronPythonTest.exe --labels=All --where:Category==IronPython --result:ironpython-net40-release-result.xml) || true

test-ironpython-debug:
	(cd bin/Debug && mono ./IronPythonTest.exe --labels=All --where:Category==IronPython --result:ironpython-net45-debug-result.xml) || true
	(cd bin/v4Debug && mono ./IronPythonTest.exe --labels=All --where:Category==IronPython --result:ironpython-net40-debug-result.xml) || true

test-cpython:
	(cd bin/Release && mono ./IronPythonTest.exe --labels=All --where:"Category==StandardCPython || Category==AllCPython" --result:cpython-net45-release-result.xml) || true
	(cd bin/v4Release && mono ./IronPythonTest.exe --labels=All -where:"Category==StandardCPython || Category==AllCPython" --result:cpython-net40-release-result.xml) || true

test-cpython-debug:
	(cd bin/Debug && mono ./IronPythonTest.exe --labels=All --where:"Category==StandardCPython || Category==AllCPython" --result:cpython-net45-debug-result.xml) || true
	(cd bin/v4Debug && mono ./IronPythonTest.exe --labels=All ---where:"Category==StandardCPython || Category==AllCPython" --result:cpython-net40-debug-result.xml) || true


test-smoke:
	(cd bin/Release && mono ./IronPythonTest.exe --labels=All --where:Category==StandardCPython --result=smoke-net45-release-result.xml) || true
	(cd bin/v4Release && mono ./IronPythonTest.exe --labels=All --where:Category==StandardCPython --result=smoke-net40-release-result.xml) || true

test-smoke-debug:
	(cd bin/Debug && mono ./IronPythonTest.exe --labels=All --where:Category==StandardCPython --result=smoke-net45-debug-result.xml) || true
	(cd bin/v4Debug && mono ./IronPythonTest.exe --labels=All --where:Category==StandardCPython --result=smoke-net40-release-result.xml) || true

test-all:
	(cd bin/Release && mono ./IronPythonTest.exe --labels=All --result=all-net45-release-result.xml) || true
	(cd bin/v4Release && mono ./IronPythonTest.exe --labels=All --result=all-net40-release-result.xml) || true

test-all-debug:
	(cd bin/Debug && mono ./IronPythonTest.exe --labels=All --result=all-result-net45.xml) || true
	(cd bin/v4Debug && mono ./IronPythonTest.exe --labels=All --result=all-result-net40.xml) || true

