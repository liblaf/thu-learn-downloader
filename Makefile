NAME  := tld

BUILD := build
DIST  := dist

SYSTEM  != python -c 'import platform; print(platform.system().lower())'
MACHINE != python -c 'import platform; print(platform.machine().lower())'

ifeq ($(SYSTEM), windows)
  EXE := .exe
else
  EXE :=
endif

DIST_TARGET := $(DIST)/$(NAME)-$(SYSTEM)-$(MACHINE)$(EXE)

all:

include make/*.mk

clean: demo-clean
	@ $(RM) --recursive --verbose $(BUILD)
	@ $(RM) --recursive --verbose $(DIST)
	@ find . -type d -name '__pycache__' -exec $(RM) --recursive --verbose '{}' +
	@ find . -type f -name '*.spec'      -exec $(RM) --verbose '{}' +

dist: $(DIST_TARGET)

setup:
	poetry install
	conda install --yes libpython-static

#####################
# Auxiliary Targets #
#####################

$(DIST_TARGET): main.py
	@ mkdir -p -v $(@D)
ifneq ($(SYSTEM), windows)
	python -m nuitka --standalone --onefile --output-filename=$(@F) --output-dir=$(@D) --remove-output  $<
else
	pyinstaller --distpath=$(DIST) --workpath=$(BUILD) --onefile --name=$(NAME)-$(SYSTEM)-$(MACHINE) $<
endif
