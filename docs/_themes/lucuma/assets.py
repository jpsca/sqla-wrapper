# -*- coding: utf-8 -*-
from os.path import join, dirname

import webassets


assets_env = webassets.Environment(
    join(dirname(__file__), 'static'),
    '/static'
)

assets_env.config['CLOSURE_COMPRESSOR_OPTIMIZATION'] = 'SIMPLE_OPTIMIZATIONS'

assets_env.register(
    'css_main',

    'styles/normalize.css',
    'styles/font-awesome.css',
    'styles/main.css',
    'styles/type.css',
    'styles/responsive.css',
    'styles/pygments.css',
    'styles/magnific-popup.css',
    'styles/print.css',

    filters='less,cssmin',
    output='styles/styles.min.css'
)

assets_env.register(
    'js_main',

    'scripts/jquery.js',
    'scripts/lodash.js',
    'scripts/doctools.js',
    'scripts/magnific-popup.js',
    'scripts/main.js',

    filters='closure_js',
    output='scripts/scripts.min.js'
)

if __name__ == '__main__':
    import sys
    from webassets import script
    script.main(sys.argv[1:], env=assets_env)
