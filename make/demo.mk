ASSETS   := assets
FRAMES   := frames
TEMPLATE := template

demo: $(ASSETS)/demo.png $(TEMPLATE)/scripts/deploy-gh-pages.sh
	bash $(TEMPLATE)/scripts/deploy-gh-pages.sh $(<D) assets

demo-clean:
	@ $(RM) --recursive --verbose $(ASSETS)
	@ $(RM) --recursive --verbose $(FRAMES)

$(ASSETS)/demo.png: $(FRAMES)/frame-025.png
	@ mkdir --parents --verbose $(@D)
	@ cp --verbose $< $@

$(FRAMES)/demo.gif: demo.tape
ifeq ($(BW_SESSION),)
	$(error Bitwarden Locked)
endif
	@ mkdir --parents --verbose $(@D)
	vhs --output=$@ $<

$(FRAMES)/frame-%.png: $(FRAMES)/demo.gif
	magick convert -coalesce $< $(@D)/frame-%03d.png
