# MakeFile for building all the docs at once.
#

.PHONY: clean publish

langs = es en

html: $(foreach lang,$(langs),html-$(lang))

html-%:
	cd $* && make html LANG=$*

htmlhelp: $(foreach lang,$(langs),htmlhelp-$(lang))

htmlhelp-%:
	cd $* && make htmlhelp LANG=$*

epub: $(foreach lang,$(langs),epub-$(lang))

epub-%:
	cd $* && make epub LANG=$*

latexpdf: $(foreach lang,$(langs),latexpdf-$(lang))

latexpdf-%:
	cd $* && make latexpdf LANG=$*

clean:
	rm -rf _build/html/es
	rm -rf _build/html/en

publishdocs: clean html
	scp -r _build/html/* jps@lucuma3:/var/www/lucumalabs/sqlawrapper/
