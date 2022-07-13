ASE_DIR=ase
DOCSET_ROOT=ase.docset
DOCSET_DOCS=$(DOCSET_ROOT)/Contents/Resources/Documents

docset:
	rm -rv $(DOCSET_DOCS) || true
	mkdir -p $(DOCSET_DOCS)
	cp -rv $(ASE_DIR)/doc/build/html/* $(DOCSET_DOCS)
	python3 scripts/build.py

doc:
	git clone https://gitlab.com/ase/ase.git $(ASE_DIR)
	python3 -m pip install -e ./ase[docs]
	$(MAKE) -C $(ASE_DIR)/doc html

clean:
	rm -rvf $(LAMMPS_DIR)
