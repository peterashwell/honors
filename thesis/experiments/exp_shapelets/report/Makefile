PROJ = standalone

all: pdf

prelim:
	pdflatex -shell-escape prelim_results.tex

pdf:
	pdflatex -shell-escape $(PROJ)
	bibtex $(PROJ)
	pdflatex $(PROJ)
	pdflatex $(PROJ)

clean:
	rm -f `find . -name '*.log'`
	rm -f `find . -name '*.dvi'`
	rm -f `find . -name '*.ps'`
	rm -f `find . -name '*.aux'`
	rm -f `find . -name '*.blg'`
	rm -f `find . -name '*.bbl'`
	rm -f `find . -name '*.toc'`
	rm -f `find . -name '*.lof'`
	rm -f `find . -name '*.lot'`
	rm -f `find . -name '*.out'`
	rm -f `find . -name '*~'`
										
