# browser: run the system's browser if available
#
define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url
from pathlib import Path
path = Path(sys.argv[1]).resolve().relative_to(Path.home())
webbrowser.open("file:///$(BROWSER_PREFIX)" + pathname2url(str(path)))
endef

export BROWSER_PYSCRIPT

.PHONY: browser
browser := python -c "$$BROWSER_PYSCRIPT"

browser-clean:
	@:

browser-sterile:
	@:
