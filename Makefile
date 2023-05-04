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

clean:
	$(RM) --recursive $(CURDIR)/build
	$(RM) --recursive $(DIST)
	$(RM) $(CURDIR)/*.spec

demo: $(CURDIR)/demo.gif

dist: $(TARGET)

install: $(TARGET_INSTALL)

poetry: $(CURDIR)/poetry.lock $(CURDIR)/requirements.txt

pretty:
	isort --profile black $(CURDIR)
	black $(CURDIR)

ALWAYS:

$(TARGET_INSTALL): $(TARGET)
	install -D --mode=u=rwx,go=rx --no-target-directory $< $@

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
	pyinstaller --onefile --name $(NAME) $(CURDIR)/main.py
