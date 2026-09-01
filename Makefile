.PHONY: pdf clean

pdf:
	latexmk main.tex

clean:
	latexmk -C main.tex
