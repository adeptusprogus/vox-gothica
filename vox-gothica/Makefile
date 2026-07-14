# Vox Gothica build rites.
PY ?= python3

.PHONY: proba pyz binarium sigillum-cogitator docker clean

proba:                      ## run the language test-suite (demo project)
	$(PY) scripts/run_proba.py

pyz:                        ## single-file gothica.pyz (needs any Python 3.10+)
	rm -rf build/zapp && mkdir -p build/zapp dist
	cp -r gothica build/zapp/gothica
	printf 'import sys\nfrom gothica.cli import main\nsys.exit(main())\n' > build/zapp/__main__.py
	$(PY) -m zipapp build/zapp -o dist/gothica.pyz -p "/usr/bin/env python3"
	chmod +x dist/gothica.pyz
	@echo "++ dist/gothica.pyz forged ++"

binarium:                   ## self-contained binary via PyInstaller (no Python on target)
	$(PY) -m pip install --quiet pyinstaller
	$(PY) -m pip install --quiet -e .
	$(PY) -m PyInstaller --onefile --name gothica \
	    --collect-submodules gothica \
	    --distpath dist --workpath build/pyi --specpath build/pyi \
	    gothica_entry.py
	./dist/gothica versio
	./dist/gothica invoco exempla/salutatio.vg --silens
	@echo "++ dist/gothica (self-contained binary for THIS platform) ++"

sigillum-cogitator:         ## seal Cogitator Arithmetica GUI (fenestra)
	$(PY) -m pip install --quiet pyinstaller
	$(PY) -m pip install --quiet -e .
	$(PY) -m gothica.cli sigillum applicata/cogitator_arithmetica/principium_fenestra.vg --fenestra --nomine CogitatorArithmetica
	@echo "++ dist/CogitatorArithmetica (Vox Gothica fenestra app) ++"

docker:                     ## fabrica execution image (gothica + terraform)
	docker build -t vox-gothica:latest .
	@echo "++ run: docker run --rm -v \$$PWD:/opus vox-gothica auguro /opus/fabrica.vg ++"

clean:
	rm -rf build dist exempla/.gothica **/__pycache__
