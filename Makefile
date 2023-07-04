BUILD := $(CURDIR)/build
DIST  := $(CURDIR)/dist
NAME  := tld

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
	@ find $(CURDIR) -type d -name '__pycache__' -exec $(RM) --recursive --verbose '{}' +
	@ find $(CURDIR) -type f -name '*.spec'      -exec $(RM) --verbose '{}' +
	$(RM) --recursive $(BUILD)
	$(RM) --recursive $(DIST)

docs: $(CURDIR)/main.py
	typer $< utils docs --name=$(NAME)

dist: $(DIST_TARGET)

pretty: black prettier

setup:
	poetry install
	conda install --yes libpython-static

#####################
# Auxiliary Targets #
#####################

$(DIST_TARGET): $(CURDIR)/main.py
ifeq ($(OS), windows)
	pyinstaller --distpath=$(DIST) --workpath=$(BUILD) --onefile --name=$(NAME)-$(SYSTEM)-$(MACHINE) $<
else
	python -m nuitka --standalone --onefile --output-filename=$(@F) --output-dir=$(@D) --remove-output  $<
endif

black:
	isort --profile black $(CURDIR)
	black $(CURDIR)

prettier: $(CURDIR)/.gitignore
	prettier --write --ignore-path=$< $(CURDIR)
