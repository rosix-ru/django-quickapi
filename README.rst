Django QuickAPI is an easy way to setup mechanism calls for Django projects.

Installation
------------

- From pypi_::

        $ pip install django-quickapi

- Or::

        $ easy_install django-quickapi

Application Setup
-----------------

- Add quickapi to `PYTHONPATH` and installed applications::

        INSTALLED_APPS = (
            ...
            'quickapi'
        )

- Add URLs entries::

        urlpatterns = patterns('',
            ...
            url(r'^api/', include('quickapi.urls', namespace='quickapi', app_name='quickapi')),
            ...
        )

- Test address in browser::

        '/api/test/'

- Create your function in views::

        from quickapi.http import JSONResponse, JSONRedirect
        from quickapi.decorators import login_required, api_required

        @api_required   # non-required
        @login_required # non-required
        api_mymethod(request):
            ''' *Documentation with markdown support* '''
            data = {'list': [1,2,3,4,5]}
            return JSONResponse(data=data)

- Register your function in settings::

        QUICKAPI_DEFINED_METHODS = {
            'mymethod': 'project.app.views.api_mymethod',
        }


*This is application tested on Django 1.4 and 1.5*

