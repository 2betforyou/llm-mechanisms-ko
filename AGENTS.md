# Repository writing rules

- Write narrative prose in `.tex` files with one complete sentence per physical source line.
- Preserve paragraph-separating blank lines and the existing structure of equations, tables, figures, TikZ, lists, and listings.
- Keep established machine learning and LLM terminology in English. Do not translate terms such as `residual stream`, `hidden state`, `attention`, `embedding`, `feature`, or `output projection` into Korean.
- Formatting-only changes must not alter non-whitespace source content or rendered PDF output.
- Run `make check-tex-format` and `make pdf` after editing prose.
