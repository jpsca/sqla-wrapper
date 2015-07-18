
==============
Sphinx-Themes
==============

Sphinx Themes for Python related projects

This repository contains Sphinx themes for Python related projects.
To use this style in your Sphinx documentation, follow
this guide:

1. Put this folder as _themes into your docs folder.  Alternatively
   you can also use git submodules to check out the contents there.

2. Add this to your conf.py and replace with your project values:

    html_theme_path = ['_themes']
    html_theme = 'lucuma'

   html_context = {
        'project': project,
        'author': author,
        'author_url': author_url,
        'github': github,
        'analytics_code': analytics_code,
        'url': project_url,
        'seo_description': description,
        'license': license,
   }

