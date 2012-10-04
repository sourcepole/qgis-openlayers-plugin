# Makefile for a PyQGIS plugin 

PLUGINNAME = openlayers_plugin

PY_FILES =

EXTRAS =

UI_FILES = openlayers_ovwidgetbase.py

RESOURCE_FILES = resources_rc.py

default: compile transup

compile: $(UI_FILES) $(RESOURCE_FILES)

%_rc.py : %.qrc
	pyrcc4 -o $@  $<

%.py : ui/%.ui
	pyuic4 -o $@ $<

%.qm : %.ts
	lrelease $<

# translation
SOURCES = openlayers_plugin.py \
          openlayers_ovwidget.py \
          openlayers_ovwidgetbase.py
TRANSLATIONS = i18n/openlayers_de.ts \
               i18n/openlayers_en.ts \
               i18n/openlayers_fr.ts
transup:
	pylupdate4 Makefile

transcompile: $(TRANSLATIONS:.ts=.qm)

# The deploy  target only works on unix like operating system where
# the Python plugin directory is located at:
# $HOME/.qgis/python/plugins
deploy-local: compile transcompile
	mkdir -p $(HOME)/.qgis/python/plugins/$(PLUGINNAME)
	cp -vf $(PY_FILES) $(HOME)/.qgis/python/plugins/$(PLUGINNAME)
	cp -vf $(UI_FILES) $(HOME)/.qgis/python/plugins/$(PLUGINNAME)
	cp -vf $(RESOURCE_FILES) $(HOME)/.qgis/python/plugins/$(PLUGINNAME)
	cp -vf $(EXTRAS) $(HOME)/.qgis/python/plugins/$(PLUGINNAME)

deploy: compile transcompile
	echo "Deploy remote repo (don't forget to push first!)"
	ssh -t root@vilan.sourcepole.ch "vserver builder exec su - builder sh -c ./qgis-plugins-update"
