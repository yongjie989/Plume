from wsgiref.simple_server import make_server
from wsgiref.validate import validator
from wsgiref import util
from string import Template
from cgi import parse_qs, escape

HOST = '127.0.0.1'
PORT = 8000
#https://github.com/ooici/ion-ux/blob/master/cilogon-wsgi/wsgi-portal/portal.wsgi.template
#http://www.google.com.tw/search?gcx=c&sourceid=chrome&ie=UTF-8&q=WSGI+myapp.url_args
#http://lucumr.pocoo.org/2007/5/21/getting-started-with-wsgi/
wrapper = Template("""
    <html><head><title>$title</title></head><body>
    $body
    </body></html>
    """)

four_oh_four = Template("""
    <html><body>
      <h1>404-ed!</h1>
      The requested URL <i>$url</i> was not found.
    </body></html>""")

pages = {
    'favicon.ico':{'title':'','body':''},
    'index': {
        'title': "Hello There",
        'body':  """This is a test of the WSGI system.
                    Perhaps you would also be interested in
                    <a href="this_page">this page</a>?"""
        },
    'this_page': {
        'title': "You're at this page",
        'body': """Hey, you're at this page.
                <a href="/">Go back</a>?"""
        }
}

html = """
<html>
<body>
   <form method="post" action="/">
      <p>
         Age: <input type="text" name="age">
         </p>
      <p>
         Hobbies:
         <input name="hobbies" type="checkbox" value="software"> Software
         <input name="hobbies" type="checkbox" value="tunning"> Auto Tunning
         </p>
      <p>
         <input type="submit" value="Submit">
         </p>
      </form>
   <p>
      Age: %s<br>
      Hobbies: %s
      </p>
   </body>
</html>"""

def get_test(environ, start_response):

   try:
      request_body_size = int(environ.get('CONTENT_LENGTH', 0))
      print request_body_size
   except (ValueError):
      request_body_size = 0

   request_body = environ['wsgi.input'].read(request_body_size)
   d = parse_qs(request_body)

   age = d.get('age', [''])[0]
   hobbies = d.get('hobbies', [])

   age = escape(age)
   hobbies = [escape(hobby) for hobby in hobbies]

   response_body = html % (age or 'Empty',
               ', '.join(hobbies or ['No Hobbies']))

   status = '200 OK'

   response_headers = [('Content-Type', 'text/html'),
                  ('Content-Length', str(len(response_body)))]
   start_response(status, response_headers)

   return [response_body]

def dump_environ(environ, start_response):
    response_body = ['%s: %s' % (key, value)
                     for key, value in sorted(environ.items())]
    response_body = '\n'.join(response_body)
    status = '200 OK'
    response_headers = [('Content-Type', 'text/plain'),('Content-Length', str(len(response_body)))]
    start_response(status, response_headers)
    return response_body

def aseanin_app(environ, start_response):
    try:    
        fn = util.shift_path_info(environ)
        if not fn:
            fn = 'index'
        response = wrapper.substitute(pages[fn])
        headers = [('Content-type','text/html')]
        status = '200 OK'
        start_response(status, headers)
        print environ['REQUEST_METHOD']
        print environ['PATH_INFO']
        return [response]
    except:
        headers = [('Content-type','text/html')]
        status = '404 Not Found'
        start_response(status, headers)
        response = four_oh_four.substitute(url=util.request_uri(environ))
    return [response]



import re
from cgi import escape

def index(environ, start_response):
    """This function will be mounted on "/" and display a link
    to the hello world page."""
    start_response('200 OK', [('Content-Type', 'text/html')])
    return ['''Hello World Application
               This is the Hello World application:

`continue <hello/>`_

''']

def hello(environ, start_response):
    """Like the example above, but it uses the name specified in the
URL."""
    args = environ['wsgi.url_args']
    print args
    if args:
        subject = escape(args[0])
    else:
        subject = 'World'
    start_response('200 OK', [('Content-Type', 'text/html')])
    return ['''Hello %(subject)s
            Hello %(subject)s!

''' % {'subject': subject}]

def not_found(environ, start_response):
    """Called if no URL matches."""
    start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
    return ['Not Found']

# map urls to functions
urls = [
    (r'^$', index),
    (r'hello/?$', hello),
    (r'hello/(.+)$', hello),
    (r'dump_environ/?$', dump_environ)
]

def application(environ, start_response):
    """
    The main WSGI application. Dispatch the current request to
    the functions from above and store the regular expression
    captures in the WSGI environment as  `myapp.url_args` so that
    the functions from above can access the url placeholders.

    If nothing matches call the `not_found` function.
    """
    path = environ.get('PATH_INFO', '').lstrip('/')
    for regex, callback in urls:
        match = re.search(regex, path)
        if match is not None:
            environ['wsgi.url_args'] = match.groups()
            return callback(environ, start_response)
    return not_found(environ, start_response)

if __name__ == '__main__':
    try:
        httpd = make_server(HOST, PORT, application)
        print 'Listening %s on port %s' % (HOST, PORT)
        httpd.serve_forever()
        httpd.handle_request()
        print dir(httpd)
    except KeyboardInterrupt:
        print 'CTRL-C caught, Stopped the Server.'
