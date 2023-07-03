ASSETS   := $(CURDIR)/assets
FRAMES   := $(CURDIR)/frames
TEMPLATE := $(CURDIR)/template

demo: $(ASSETS)/demo.png $(TEMPLATE)/scripts/deploy-gh-pages.sh
	bash $(TEMPLATE)/scripts/deploy-gh-pages.sh $(dir $<) assets

demo-clean:
	$(RM) --recursive $(ASSETS)
	$(RM) --recursive $(FRAMES)

$(ASSETS) $(FRAMES):
	@ mkdir --parents --verbose $@

$(ASSETS)/demo.png: $(FRAMES)/frame-100.png | $(ASSETS)
	@ install -D --mode="u=rw,go=r" --no-target-directory --verbose $< $@

$(FRAMES)/demo.gif: $(CURDIR)/demo.tape | $(FRAMES)
ifeq ($(BW_SESSION),)
	$(error Bitwarden Locked)
else
	vhs --output=$@ $<
endif

$(FRAMES)/frame-%.png: $(FRAMES)/demo.gif
	magick convert -coalesce $< $(@D)/frame-%03d.png
