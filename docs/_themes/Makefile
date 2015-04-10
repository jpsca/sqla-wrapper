
extract:
	pybabel extract -F babel.cfg -o _locale/lucuma.pot lucuma

compile:
	msgfmt.py _locale/es/LC_MESSAGES/*.po
	msgfmt.py _locale/en/LC_MESSAGES/*.po

clean:
	rm -f _locale/lucuma.pot
	rm -f _locale/es/LC_MESSAGES/*.mo
	rm -f _locale/en/LC_MESSAGES/*.mo
