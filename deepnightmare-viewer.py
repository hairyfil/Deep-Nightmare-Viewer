#
#
#

import sys
from flask import Flask, render_template, redirect
import os
from PIL import Image

os.environ["BOTO_CONFIG"] = ".boto"
import boto

DOWNLOADPATH = "tmp/"
OUTPUTPATH = "tmp/"

port = int(os.getenv("PORT"))
app = Flask(__name__)

#
# Uses flask templates
# combine with bootstrap css
# docs from https://www.tutorialspoint.com/flask/flask_templates.htm
#

@app.route('/')
def flasktemplate():
	s3_session = boto.connect_s3()

	before_bucketname 			= "deepnightmare-before"
	after_bucketname 			= "deepnightmare-after"
	before_thumbnail_bucketname = "deepnightmare-before-thumbnails"
	after_thumbnail_bucketname 	= "deepnightmare-after-thumbnails"

	before_bucket 				= s3_session.get_bucket(before_bucketname)
	after_bucket 				= s3_session.get_bucket(after_bucketname)
	before_thumbnail_bucket 	= s3_session.get_bucket(before_thumbnail_bucketname)
	after_thumbnail_bucket 		= s3_session.get_bucket(after_thumbnail_bucketname)
	
	my_dynamic_table = "<CENTER><TABLE align=\"center\">"
	
	# collect all photos from the before bucket

	for photo_before in before_bucket.list():
		photo_before_name 			= str(photo_before.key).replace(".jpg", "")
		photo_before_url 			= "https://{1}.{0}/{2}.jpg".format(s3_session.server_name(), before_bucketname, photo_before_name)
		photo_before_thumbnail_name = photo_before_name + ".jpg-thumbnail.jpg"
		photo_before_thumbnail_url 	= "https://{1}.{0}/{2}".format(s3_session.server_name(), before_thumbnail_bucketname, photo_before_thumbnail_name)
		my_dynamic_table += "<TR><TD align=\"center\"><a href=\"{}\"><image src = \"{}\"></a></TD>".format(photo_before_url, photo_before_thumbnail_url)

		print ("photo_before_name = ", photo_before_name)
		print ("photo_before_thumbnail_name = ", photo_before_thumbnail_name)
		sys.stdout.flush()

		for photo_after_thumbnail in after_thumbnail_bucket.get_all_keys(prefix=photo_before_name):
			photo_after_name = str(photo_after_thumbnail.key).replace("-thumbnail.jpg", "")
			photo_after_thumbnail_name = str(photo_after_thumbnail.key)
			
			print (photo_before_thumbnail_name + " - " + photo_after_thumbnail_name)
			sys.stdout.flush()
			photo_after_url 			= "https://{}.{}/{}".format(after_bucketname, s3_session.server_name(), photo_after_name)
			photo_after_thumbnail_url 	= "https://{}.{}/{}".format(after_thumbnail_bucketname, s3_session.server_name(), photo_after_thumbnail_name)

			print ("photo_after_url 			= [", photo_after_url, "]")
			print ("photo_after_thumbnail_url 	= [", photo_after_thumbnail_url, "]")
			print ("")
			sys.stdout.flush()
			
			my_dynamic_table += "<TD align=\"center\"><a href=\"{}\"><image src = \"{}\"></a></TD>".format(photo_after_url, photo_after_thumbnail_url)
		
		my_dynamic_table += "</TR>"


	# now parse the predreamed images & thumbnails
	
	print ("Parsing pre-dreamed images now...")
	sys.stdout.flush()
	
	predreamed_before_bucketname 			= "predreamed-before"
	predreamed_after_bucketname 			= "predreamed-after"
	predreamed_before_thumbnail_bucketname 	= "predreamed-before-thumbnails"
	predreamed_after_thumbnail_bucketname 	= "predreamed-after-thumbnails"

	predreamed_before_bucket 				= s3_session.get_bucket(predreamed_before_bucketname)
	predreamed_after_bucket 				= s3_session.get_bucket(predreamed_after_bucketname)
	predreamed_before_thumbnail_bucket 		= s3_session.get_bucket(predreamed_before_thumbnail_bucketname)
	predreamed_after_thumbnail_bucket 		= s3_session.get_bucket(predreamed_after_thumbnail_bucketname)

	for photo_before in predreamed_before_bucket.list():
		photo_before_name 			= str(photo_before.key)
		photo_before_url 			= "https://{1}.{0}/{2}".format(s3_session.server_name(), predreamed_before_bucketname, photo_before_name)
		photo_before_thumbnail_name = str(photo_before.key) + "-thumbnail.jpg"
		photo_before_thumbnail_url 	= "https://{1}.{0}/{2}".format(s3_session.server_name(), predreamed_before_thumbnail_bucketname, photo_before_thumbnail_name)
		my_dynamic_table += "<TR><TD align=\"center\"><a href=\"{}\"><image src = \"{}\"></a></TD>".format(photo_before_url, photo_before_thumbnail_url)

		# print ("photo_before_name           = ", photo_before_name)
		# print ("photo_before_thumbnail_name = ", photo_before_thumbnail_name)
		# sys.stdout.flush()

		for photo_after in predreamed_after_bucket.get_all_keys(prefix=photo_before_name):
			photo_after_name 			= str(photo_after.key)
			photo_after_thumbnail_name 	= photo_after_name + "-thumbnail.jpg"

			# print ("photo_after_name           = ", photo_after_name)
			# print ("photo_after_thumbnail_name = ", photo_after_thumbnail_name)
			# sys.stdout.flush()
			
			
			# print (photo_before_thumbnail_name + " - " + photo_after_thumbnail_name)
			sys.stdout.flush()
			
			photo_after_thumbnail_url 	= "https://{}.{}/{}".format(predreamed_after_thumbnail_bucketname, s3_session.server_name(), photo_after_thumbnail_name)
			photo_after_url 			= "https://{}.{}/{}".format(predreamed_after_bucketname, s3_session.server_name(), photo_after_name)

			# print ("photo_after_url 			= [", photo_after_url, "]")
			# print ("photo_after_thumbnail_url 	= [", photo_after_thumbnail_url, "]")
			# print ("")
			# sys.stdout.flush()
			
			my_dynamic_table += "<TD align=\"center\"><a href=\"{}\"><image src = \"{}\"></a></TD>".format(photo_after_url, photo_after_thumbnail_url)
		
		my_dynamic_table += "</TR>"

	my_dynamic_table += "</TABLE></CENTER>"

	return render_template('album.html', mytable = my_dynamic_table)

#
# create thumbnail images for the before & after buckets
#

@app.route('/create-thumbnails')
def create_thumbnails():
	
	s3_session = boto.connect_s3()

	before_bucketname 						= "deepnightmare-before"
	after_bucketname 						= "deepnightmare-after"

	before_thumbnail_bucketname 			= "deepnightmare-before-thumbnails"
	after_thumbnail_bucketname 				= "deepnightmare-after-thumbnails"

	before_bucket 							= s3_session.get_bucket(before_bucketname)
	after_bucket 							= s3_session.get_bucket(after_bucketname)
	before_thumbnail_bucket 				= s3_session.get_bucket(before_thumbnail_bucketname)
	after_thumbnail_bucket 					= s3_session.get_bucket(after_thumbnail_bucketname)
	
	page_head = "<HTML><BODY><HR><CENTER><H1>Generating Thumbnails</H1><HR></CENTER>"
	page_mid = "<CENTER><TABLE><TR>"
	page_foot = "<HR></BODY>Thank you for visiting</HTML>"

	#
	# collect all photos from the before bucket & create thumbnails
	#

	for photo in before_bucket.list():
		photo_name = str(photo.key)
		photo_thumbnail_name = photo_name + "-thumbnail.jpg"
		photo_path = "tmp/" + photo_name
		photo_thumbnail_path = "thumbnails/" + photo_thumbnail_name 

		photo.get_contents_to_filename(photo_path)

		size = 256, 256
		im = Image.open(photo_path)
		im.thumbnail(size)
		im.save(photo_thumbnail_path, "JPEG")

		print ("downloaded photo_path = ", photo_path)
		print ("created thumbnail     = ", photo_thumbnail_path)
		sys.stdout.flush()

		key = before_thumbnail_bucket.new_key(photo_thumbnail_name)
		key.set_contents_from_filename(photo_thumbnail_path)
		key.set_acl('public-read')

	#
	# collect all photos from the after bucket & create thumbnails
	#

	for photo in after_bucket.list():
		photo_name = str(photo.key)
		photo_thumbnail_name = photo_name + "-thumbnail.jpg"
		photo_path = "tmp/" + photo_name
		photo_thumbnail_path = "thumbnails/" + photo_thumbnail_name 

		photo.get_contents_to_filename(photo_path)

		size = 256, 256
		im = Image.open(photo_path)
		im.thumbnail(size)
		im.save(photo_thumbnail_path, "JPEG")

		print ("downloaded photo_path = ", photo_path)
		print ("created thumbnail     = ", photo_thumbnail_path)
		sys.stdout.flush()

		key = after_thumbnail_bucket.new_key(photo_thumbnail_name)
		key.set_contents_from_filename(photo_thumbnail_path)
		key.set_acl('public-read')

	return redirect ("/")

#
# create thumbnail images for the predreamed before & after buckets
#

@app.route('/create-predreamed-thumbnails')
def create_predreamed_thumbnails():
	
	s3_session = boto.connect_s3()

	predreamed_before_bucketname 			= "predreamed-before"
	predreamed_after_bucketname 			= "predreamed-after"

	predreamed_before_thumbnail_bucketname 	= "predreamed-before-thumbnails"
	predreamed_after_thumbnail_bucketname 	= "predreamed-after-thumbnails"

	predreamed_before_bucket 				= s3_session.get_bucket(predreamed_before_bucketname)
	predreamed_after_bucket 				= s3_session.get_bucket(predreamed_after_bucketname)
	predreamed_before_thumbnail_bucket 		= s3_session.get_bucket(predreamed_before_thumbnail_bucketname)
	predreamed_after_thumbnail_bucket 		= s3_session.get_bucket(predreamed_after_thumbnail_bucketname)
	
	page_head = "<HTML><BODY><HR><CENTER><H1>Generating Thumbnails for Pre-Dreamed Images</H1><HR></CENTER>"
	page_mid = "<CENTER><TABLE><TR>"
	page_foot = "<HR></BODY>Thank you for visiting</HTML>"

	#
	# collect all photos from the predreamed before bucket & create thumbnails
	#

	for photo in predreamed_before_bucket.list():
		photo_name 				= str(photo.key)
		photo_thumbnail_name 	= photo_name + "-thumbnail.jpg"
		photo_path 				= "tmp/" + photo_name
		photo_thumbnail_path 	= "thumbnails/" + photo_thumbnail_name 

		photo.get_contents_to_filename(photo_path)

		size = 256, 256
		im = Image.open(photo_path)
		im.thumbnail(size)
		im.save(photo_thumbnail_path, "JPEG")

		print ("downloaded photo_path = ", photo_path)
		print ("created thumbnail     = ", photo_thumbnail_path)
		sys.stdout.flush()

		key = predreamed_before_thumbnail_bucket.new_key(photo_thumbnail_name)
		key.set_contents_from_filename(photo_thumbnail_path)
		key.set_acl('public-read')

	#
	# collect all photos from the predreamed after bucket & create thumbnails
	#

	for photo in predreamed_after_bucket.list():
		photo_name 				= str(photo.key)
		photo_thumbnail_name 	= photo_name + "-thumbnail.jpg"
		photo_path 				= "tmp/" + photo_name
		photo_thumbnail_path 	= "thumbnails/" + photo_thumbnail_name 

		photo.get_contents_to_filename(photo_path)

		size = 256, 256
		im = Image.open(photo_path)
		im.thumbnail(size)
		im.save(photo_thumbnail_path, "JPEG")

		print ("downloaded photo_path = ", photo_path)
		print ("created thumbnail     = ", photo_thumbnail_path)
		sys.stdout.flush()

		key = predreamed_after_thumbnail_bucket.new_key(photo_thumbnail_name)
		key.set_contents_from_filename(photo_thumbnail_path)
		key.set_acl('public-read')

	return ""

#
#
#

@app.route('/old')
def s3_sessionlist():
	
	s3_session = boto.connect_s3()

	before_bucketname 			= "deepnightmare-before"
	after_bucketname 			= "deepnightmare-after"
	before_thumbnail_bucketname = "deepnightmare-before-thumbnails"
	after_thumbnail_bucketname 	= "deepnightmare-after-thumbnails"

	before_bucket 				= s3_session.get_bucket(before_bucketname)
	after_bucket 				= s3_session.get_bucket(after_bucketname)
	before_thumbnail_bucket 	= s3_session.get_bucket(before_thumbnail_bucketname)
	after_thumbnail_bucket 		= s3_session.get_bucket(after_thumbnail_bucketname)
	
	page_head = "<HTML><BODY><HR><CENTER><H1>Deep Nightmares</H1><HR></CENTER>"
	page_mid = "<CENTER><TABLE align=\"center\">"
	page_foot = "<HR></BODY>Thank you for visiting</HTML>"

	# collect all photos from the bucket

	for photo_before in before_bucket.list():
		photo_before_name 			= str(photo_before.key)
		photo_before_url 			= "https://{1}.{0}/{2}".format(s3_session.server_name(), before_bucketname, photo_before_name)
		photo_before_thumbnail_name = str(photo_before.key) + "-thumbnail.jpg"
		photo_before_thumbnail_url 	= "https://{1}.{0}/{2}".format(s3_session.server_name(), before_thumbnail_bucketname, photo_before_thumbnail_name)
		page_mid += "<TR><TD align=\"center\"><a href=\"{}\"><image src = \"{}\"></a></TD>".format(photo_before_url, photo_before_thumbnail_url)

		# print ("photo_before_thumbnail_name = ", photo_before_thumbnail_name)
		# sys.stdout.flush()

		for photo_after_thumbnail in after_thumbnail_bucket.get_all_keys(prefix=photo_before.key):
			photo_after_name = str(photo_after_thumbnail.key).replace("-thumbnail.jpg", "")
			photo_after_thumbnail_name = str(photo_after_thumbnail.key)
			
			# print (photo_before_thumbnail_name + " - " + photo_after_thumbnail_name)
			# sys.stdout.flush()
			photo_after_url 			= "https://{}.{}/{}".format(after_bucketname, s3_session.server_name(), photo_after_name)
			photo_after_thumbnail_url 	= "https://{}.{}/{}".format(after_thumbnail_bucketname, s3_session.server_name(), photo_after_thumbnail_name)

			# print ("photo_after_url 			= [", photo_after_url, "]")
			# print ("photo_after_thumbnail_url 	= [", photo_after_thumbnail_url, "]")
			# print ("")
			# sys.stdout.flush()
			
			page_mid += "<TD align=\"center\"><a href=\"{}\"><image src = \"{}\"></a></TD>".format(photo_after_url, photo_after_thumbnail_url)
		
		page_mid += "</TR>"
	page_mid += "</TABLE></CENTER>"

	return page_head + page_mid + page_foot

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=port)