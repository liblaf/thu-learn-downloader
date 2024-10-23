default: gen-init

.PHONY: gen-init
gen-init: scripts/gen-init.sh
	@ "$<"
