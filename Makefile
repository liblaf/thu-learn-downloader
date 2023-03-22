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

TARGET := $(DIST)/$(NAME)$(EXE)

build: $(TARGET)

clean:
	$(RM) --recursive $(CURDIR)/build
	$(RM) --recursive $(DIST)
	$(RM) $(CURDIR)/*.spec

demo: $(CURDIR)/demo.gif

install: $(TARGET) | $(BIN)
	install --target-directory=$(BIN) $<

pretty:
	isort --profile black $(CURDIR)
	black $(CURDIR)

rename: $(TARGET)
ifneq ($(and $(OS), $(ARCH)), )
	mv $< $(DIST)/$(NAME)-$(OS)-$(ARCH)$(EXE)
endif

$(TARGET):
	pyinstaller --distpath $(DIST) --onefile --name $(NAME) $(CURDIR)/main.py

$(BIN):
	mkdir --parents $@

$(CURDIR)/demo.gif: $(CURDIR)/demo.tape
ifeq ($(BW_SESSION),)
	$(error Bitwarden Locked)
else
	vhs < $<
endif
