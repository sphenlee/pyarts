build:
	cd rust ; cargo build ; cd ..

build-release:
	cd rust ; cargo build --release ; cd ..

run LOG="yarts=info,pyarts=info":
	#!/bin/sh
	. .ve/bin/activate
	export RUST_LOG={{LOG}}
	python rsmain.py

