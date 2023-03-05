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

.PHONY: build
build:
	pyinstaller --distpath $(DIST) --onefile --name $(NAME) $(CURDIR)/main.py

clean:
	$(RM) --recursive $(CURDIR)/build
	$(RM) --recursive $(CURDIR)/outputs
	$(RM) --recursive $(DIST)
	$(RM) $(CURDIR)/*.spec

demo:
ifeq ($(BW_SESSION),)
	$(error Bitwarden Locked)
else
	vhs < $(CURDIR)/demo.tape
endif

install: build
	install --target-directory=$(BIN) $(TARGET)

pretty:
	isort --profile black $(CURDIR)
	black $(CURDIR)

rename: build
ifneq ($(and $(OS), $(ARCH)), )
	mv $(TARGET) $(DIST)/$(NAME)-$(OS)-$(ARCH)$(EXE)
endif
