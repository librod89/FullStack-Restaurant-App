from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem

#Create session and connect to DB
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class webserverHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			if self.path.endswith("/restaurants") or self.path.endswith("/restaurants/"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = ""
				output += "<html><body>"
				output += "<h1><a href='/restaurants/new'>Add a new restaurant</a></h1>"
				restaurants = session.query(Restaurant).all()
				for restaurant in restaurants:
					output += "<h3>%s</h3>" % restaurant.name
					output += "<a href='/restaurants/%s/edit'>Edit</a><br>" % restaurant.id
					output += "<a href='/restaurants/%s/delete'>Delete</a>" % restaurant.id
					output += "<br>"

				output += "</body></html>"
				self.wfile.write(output)
				#print output
				return

			if self.path.endswith("/restaurants/new"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				output = ""
				output += "<html><body>"
				output += "<form method='POST' enctype='multipart/form-data' action='create'><h2>Enter the new restaurant: </h2><input name='message' type='text'><input type='submit' value='Submit'></form>"
				output +="</body></html>"
				self.wfile.write(output)
				#print output
				return

			if self.path.endswith("edit"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				path = self.path.split('/')
				_id = path[2]
				restaurant = session.query(Restaurant).filter_by(id = _id).one()
				
				action = self.path + "/update"
				output = ""
				output += "<html><body>"
				output += "<form method='POST' enctype='multipart/form-data' action='%s'><h2>Update restaurant name: </h2><input name='message' type='text' placeholder='%s'><input type='submit' value='Submit'></form>" % (action, restaurant.name.replace("'", ""))
				output +="</body></html>"
				self.wfile.write(output)
				#print output
				return

			if self.path.endswith("delete"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				
				path = self.path.split('/')
				_id = path[2]
				restaurant = session.query(Restaurant).filter_by(id = _id).one()

				output = "<html><body>"
				output += "<h3>Are you sure you want to delete %s from the list?</h3>" % restaurant.name
				output += "<form method='POST' action='%s'><input type='submit' value='Delete'></form>" % self.path
				output += "</body></html>"
				self.wfile.write(output)
				return
				

		except IOError:
			self.send_error(404, "File Not Found %s" % self.path)
	def do_POST(self):
		try:
			ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
			if ctype == 'multipart/form-data':
				fields = cgi.parse_multipart(self.rfile, pdict)
				messagecontent = fields.get('message')
			if self.path.endswith("create"):
				restaurant = Restaurant(name=messagecontent[0])
				session.add(restaurant)
			if self.path.endswith("update"):
				path = self.path.split('/')
				_id = path[2]
				restaurant = session.query(Restaurant).filter_by(id = _id).one()
				restaurant.name = messagecontent[0]
				session.add(restaurant)
			if self.path.endswith("delete"):
				path = self.path.split('/')
				_id = path[2]
				restaurant = session.query(Restaurant).filter_by(id = _id).one()
				session.delete(restaurant)
				
			session.commit()
			self.send_response(301)
			self.send_header("Location", "/restaurants")
			self.end_headers()

		except Exception as e:
			print e

def main():
	try:
		port = 8080
		server = HTTPServer(('', port), webserverHandler)
		print "Web server running on port %s" % port
		server.serve_forever()
	except KeyboardInterrupt:
		print "^C entered, stopping web server..."
		server.socket.close()

if __name__ == '__main__':
	main()
