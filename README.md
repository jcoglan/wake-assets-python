# wake_assets

This package helps you render links to assets managed using
[wake](http://github.com/jcoglan/wake). It's easy to set up and works with any
Python web framework.


## Usage

These examples are based on the [wake example build
config](https://github.com/jcoglan/wake#usage).

#### At boot time

When your app boots, create an instance of `Assets` and keep this object around
through the lifetime of the app process. For example, in Django:

```python
# In your site's settings.py

import os.path
from wake_assets import Assets

WAKE_ASSETS = Assets(
    wake  = os.path.join(os.getcwd(), 'node_modules', '.bin', 'wake'),
    root  = os.getcwd(),
    mode  = 'targets',
    cache = True,
)
```

The options are:

* `wake` - the path to your `wake` executable
* `root` - the document root of your application
* `mode` - `sources` if you want to render links to source files, `targets`
  if you want optimised files
* `cache` - whether to cache `wake` metadata that's read from disk

#### At request time

On each request, create a renderer from your `Assets` instance. This renderer
takes per-request tag creation settings and provides methods for generating
HTML. In Django, you might do this using a middleware, and a context processor
to add the renderer to the template context. Start by creating an app skeleton:

```
$ mkdir -p assets/templatetags
$ touch assets/models.py assets/templatetags/__init__.py
```

Then add this to the app you just created:

```python
# assets/__init__.py

import json
import os
from django.conf import settings

CONFIG_PATH = os.path.join(os.getcwd(), 'package.json')
ASSET_HOSTS = json.loads(open(CONFIG_PATH).read())['wake']['css']['hosts']

class AssetsMiddleware:
    def process_request(self, request):
        request.assets = settings.WAKE_ASSETS.renderer(
            builds = {
                'css':        'ssl' if request.is_secure else 'min',
                'javascript': 'min',
                'binary':     'min',
            },
            hosts  = ASSET_HOSTS['production']['https' if request.is_secure else 'http'],
            inline = False,
        )

def assets_context(request):
    return {'assets': request.assets}
```

Adding `assets.AssetsMiddleware` to `MIDDLEWARE_CLASSES` and
`assets.assets_context` to `TEMPLATE_CONTEXT_PROCESSORS` will wire these into
your stack.

The options are:

* `builds` - which build to use for each asset type, the default for each is
  `min`
* `hosts` - the set of asset hosts to use for rendering links, the default is
  an empty list
* `inline` - whether to render assets inline so the browser does not make
  additional requests for them, default is `False`

#### In your templates

With this helper in place, you can render links to JavaScript, CSS and images:

```python
assets.include_js('scripts.js')
# => '<script type="text/javascript" src="/assets/scripts-bb210c6.js"></script>'

assets.include_css('style.css')
# => '<link rel="stylesheet" type="text/css" href="/assets/styles-5a2ceb1.css">'

assets.include_image('logo.png', html={'alt': 'Logo'})
# => '<img src="/assets/logo-2fa8d38.png" alt="Logo">'
```

You can pass the `inline` option to any of these to override the per-request
`inline` setting:

```python
assets.include_js('scripts.js', inline=True)
# => '<script type="text/javascript">alert("Hello, world!")</script>'
```

For Django, you should bind these to custom template tags. Add the following to
`assets/templatetags/asset_tags.py`:

```python
# assets/templatetags/asset_tags.py

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag(takes_context=True)
def include_css(context, *names, **options):
    assets = context['assets']
    return mark_safe(assets.include_css(*names, **options))

@register.simple_tag(takes_context=True)
def include_image(context, *names, **options):
    assets = context['assets']
    return mark_safe(assets.include_image(*names, **options))

@register.simple_tag(takes_context=True)
def include_js(context, *names, **options):
    assets = context['assets']
    return mark_safe(assets.include_js(*names, **options))
```

Adding `assets` to `INSTALLED_APPS` will make these tags available in templates.
Use them like this:

```
{% load asset_tags %}

{% include_js 'scripts.js' %}

{% include_image 'logo.png' inline=True %}
```


## License

(The MIT License)

Copyright (c) 2013 James Coglan

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the 'Software'), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

