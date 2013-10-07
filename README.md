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

from wake_assets import Assets

WAKE_ASSETS = Assets(mode='targets', cache=True)
```

The options are:

* `wake` - the path to your `wake` executable
* `root` - the document root of your application
* `mode` - `sources` if you want to render links to source files, `targets`
  if you want optimised files
* `cache` - whether to cache `wake` metadata that's read from disk

#### At request time

On each request, create a renderer from your `Assets` instance. This renderer
takes per-request tag creation settings.

```python
config_path = os.path.join(os.getcwd(), 'package.json')
asset_hosts = json.loads(open(config_path).read())['wake']['css']['hosts']

secure = request.is_secure

assets = settings.WAKE_ASSETS.renderer(
    builds = {'css': 'ssl' if secure else 'min'},
    hosts  = asset_hosts['production']['https' if secure else 'http'],
    inline = False,
)
```

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


## License

(The MIT License)

Copyright (c) 2013 James Coglan, Songkick

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

