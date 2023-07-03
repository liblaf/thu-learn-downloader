BIN  := $(HOME)/.local/bin
DIST := $(CURDIR)/dist
NAME := tld

OS   != echo $(RUNNER_OS)   | tr '[:upper:]' '[:lower:]'
ARCH != echo $(RUNNER_ARCH) | tr '[:upper:]' '[:lower:]'

ifneq ($(and $(OS), $(ARCH)),)
	NAME := $(NAME)-$(OS)-$(ARCH)
endif

ifeq ($(OS), windows)
	EXE := .exe
else
	EXE :=
endif

TARGET         := $(DIST)/$(NAME)$(EXE)
TARGET_INSTALL := $(BIN)/$(NAME)$(EXE)

all:

include make/*.mk

clean: demo-clean
	@ find $(CURDIR) -type d -name '__pycache__' -exec $(RM) --recursive --verbose '{}' +
	@ find $(CURDIR) -type f -name '*.spec'      -exec $(RM) --verbose '{}' +
	$(RM) --recursive $(CURDIR)/build
	$(RM) --recursive $(DIST)

docs: $(CURDIR)/main.py
	typer $< utils docs --name=$(NAME)

dist: $(TARGET)

install: $(TARGET_INSTALL)

pretty: black prettier

#####################
# Auxiliary Targets #
#####################

black:
	isort --profile black $(CURDIR)
	black $(CURDIR)

prettier: $(CURDIR)/.gitignore
	prettier --write --ignore-path=$< $(CURDIR)

$(TARGET_INSTALL): $(TARGET)
	@ install -D --mode="u=rwx,go=rx" --no-target-directory --verbose $< $@

$(CURDIR)/demo.gif: $(CURDIR)/demo.tape
ifeq ($(BW_SESSION),)
	$(error Bitwarden Locked)
else
	vhs --output=$@ $<
endif

$(TARGET): $(CURDIR)/main.py
ifeq ($(OS), windows)
	pyinstaller --distpath=$(DIST) --workpath=$(CURDIR)/build --onefile --name=$(NAME) $<
else
	python -m nuitka --standalone --onefile --output-filename=$(NAME) --output-dir=$(DIST) --remove-output $<
endif
