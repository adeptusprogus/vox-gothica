# Vox Gothica build rites.
PY ?= python3

.PHONY: proba pyz binarium docker clean

proba:                      ## run the language test-suite (demo project)
	$(PY) -m gothica proba --dir demo/probationes
	$(PY) -m gothica invoco exempla/salutatio.vg --silens
	$(PY) -m gothica invoco exempla/litania_numerorum.vg --silens >/dev/null
	$(PY) -m gothica invoco exempla/census_servitorum.vg --silens >/dev/null
	$(PY) -m gothica scribe-solum exempla/fabrica_interretialis.vg --silens
	@echo "++ omnia sancta ++"

pyz:                        ## single-file gothica.pyz (needs any Python 3.10+)
	rm -rf build/zapp && mkdir -p build/zapp dist
	cp -r gothica build/zapp/gothica
	printf 'import sys\nfrom gothica.cli import main\nsys.exit(main())\n' > build/zapp/__main__.py
	$(PY) -m zipapp build/zapp -o dist/gothica.pyz -p "/usr/bin/env python3"
	chmod +x dist/gothica.pyz
	@echo "++ dist/gothica.pyz forged ++"

binarium:                   ## true native-ish binary via PyInstaller (like Go, one file, no Python needed)
	$(PY) -m pip install --quiet pyinstaller
	$(PY) -m PyInstaller --onefile --name gothica \
	    --collect-submodules gothica \
	    --distpath dist --workpath build/pyi --specpath build/pyi \
	    gothica/__main__.py
	@echo "++ dist/gothica (self-contained binary for THIS platform) ++"
	@echo "++ build on each OS you target: macOS/Linux/Windows ++"

docker:                     ## fabrica execution image (gothica + terraform)
	docker build -t vox-gothica:latest .
	@echo "++ run: docker run --rm -v \$$PWD:/opus vox-gothica auguro /opus/fabrica.vg ++"

clean:
	rm -rf build dist exempla/.gothica **/__pycache__
