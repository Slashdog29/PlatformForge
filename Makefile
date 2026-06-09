.PHONY: build clean run

build:
	pyinstaller --onefile main.py --name platformforge

clean:
	rm -rf build dist __pycache__
	rm -f platformforge.spec

run:
	python main.py