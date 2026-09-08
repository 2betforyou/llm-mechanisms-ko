.PHONY: pdf clean format-tex check-tex-format

TEX_PROSE_FILES := $(shell find frontmatter chapters appendices -name '*.tex' -print)

pdf:
	latexmk main.tex

format-tex:
	python3 scripts/format_tex_prose.py --write $(TEX_PROSE_FILES)

check-tex-format:
	python3 scripts/format_tex_prose.py --check $(TEX_PROSE_FILES)

clean:
	latexmk -C main.tex
