BIN  := $(HOME)/.local/bin
DIST := $(CURDIR)/dist
NAME := tld

OS   := $(shell echo $(RUNNER_OS)   | tr '[:upper:]' '[:lower:]')
ARCH := $(shell echo $(RUNNER_ARCH) | tr '[:upper:]' '[:lower:]')
ifeq ($(OS), windows)
	EXE := .exe
else
	EXE :=
endif

TARGET         := $(DIST)/$(NAME)$(EXE)
TARGET_INSTALL := $(BIN)/$(NAME)$(EXE)
TARGET_RENAME  := $(DIST)/$(NAME)-$(OS)-$(ARCH)$(EXE)

build: $(TARGET)

clean:
	$(RM) --recursive $(CURDIR)/build
	$(RM) --recursive $(DIST)
	$(RM) $(CURDIR)/*.spec

demo: $(CURDIR)/demo.gif

deps: $(CURDIR)/poetry.lock $(CURDIR)/requirements.txt

install: $(TARGET_INSTALL)

pretty:
	isort --profile black $(CURDIR)
	black $(CURDIR)

rename: $(TARGET_RENAME)

ALWAYS:

$(TARGET_INSTALL): $(TARGET)
	install -D --mode=u=rwx,go=rx --no-target-directory $< $@

$(TARGET_RENAME): $(TARGET)
	mv $< $@

$(CURDIR)/demo.gif: $(CURDIR)/demo.tape
ifeq ($(BW_SESSION),)
	$(error Bitwarden Locked)
else
	vhs < $<
endif

$(CURDIR)/poetry.lock: ALWAYS
	poetry lock

$(CURDIR)/requirements.txt: $(CURDIR)/poetry.lock
	poetry export --output=$@ --without-hashes --without-urls

$(TARGET):
	pyinstaller --distpath $(DIST) --onefile --name $(NAME) $(CURDIR)/main.py
