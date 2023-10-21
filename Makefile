NAME  := tld

ASSETS := assets
BUILD  := build
DIST   := dist

SYSTEM  != python -c 'import platform; print(platform.system().lower())'
MACHINE != python -c 'import platform; print(platform.machine().lower())'

ifeq ($(SYSTEM), windows)
  EXE := .exe
else
  EXE :=
endif

DIST_TARGET := $(DIST)/$(NAME)-$(SYSTEM)-$(MACHINE)$(EXE)

all:

clean:
	@ $(RM) --recursive --verbose $(ASSETS)
	@ $(RM) --recursive --verbose $(BUILD)
	@ $(RM) --recursive --verbose $(DIST)
	@ $(RM) --verbose out.gif
	@ find . -type d -name '__pycache__' -exec $(RM) --recursive --verbose '{}' +
	@ find . -type f -name '*.spec'      -exec $(RM) --verbose '{}' +

demo: $(ASSETS)/demo.png

demo-deploy: $(ASSETS)/demo.png scripts/deploy-gh-pages.sh
	bash scripts/deploy-gh-pages.sh $(ASSETS) assets

dist: $(DIST_TARGET)

setup:
	poetry install
	conda install --yes libpython-static

#####################
# Auxiliary Targets #
#####################

$(ASSETS)/demo.png: demo.tape
	@ mkdir --parents --verbose $(@D)
	vhs $<

$(DIST_TARGET): main.py
	@ mkdir --parents --verbose $(@D)
ifneq ($(SYSTEM), windows)
	python -m nuitka --standalone --onefile --output-filename=$(@F) --output-dir=$(@D) --remove-output  $<
else
	pyinstaller --distpath=$(DIST) --workpath=$(BUILD) --onefile --name=$(NAME)-$(SYSTEM)-$(MACHINE) $<
endif
