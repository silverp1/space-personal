from event import *
from log import *
from domfunctions import connect 

import data
import libvirt
import datetime
import config
import os

def sync_status():
    conn = connect()
    real_status = conn.listDefinedDomains()
    
    servers = data.get_all_servers()

    message_sync = "Syncing real state with database states."
    create_log(message_sync, 1)

    for server in servers:
        real_id = "vm%s" % str(server['_id'])
        if server['state'] == 0 and real_id not in real_status:
            message = "Checked %s, DB says it should not be running, but it is running." % real_id
            create_log(message, 2)

            inconsistent_event(server['_id'])
            
            data.set_server_inconsistent(server['_id'], 1)
        elif server['state'] == 1 and real_id in real_status:
            message = "Checked %s, DB says it should be running, but is is not running." % real_id
            create_log(message, 2)
            
            inconsistent_event(server['_id'])
    
            data.set_server_inconsistent(server['_id'], 1)

def import_images():
    #images = data.get_all_images()
    filesystem_images = [ f for f in os.listdir(config.image_path) if os.path.isfile(os.path.join(config.image_path,f)) ]
    message = "Image sync initated."
    create_log(message, 1)
    #print poop
    for image in filesystem_images:
        images = data.get_all_images()
        print image
        state = 0
        for existing_image in images:
            print "image testing is: %s" % str(os.path.splitext(image)[0])
            print "existing_image['name']: %s" % str(existing_image['name'])
            if os.path.splitext(image)[0] == existing_image['name']:
                print "found match"
                state = 1
        if state == 0:
            # we need to add it
            image_name = os.path.splitext(image)[0]
            image_path = "%s/%s" % (str(config.image_path), str(image))
            image_size = os.path.getsize(image_path)
            message2 = "Found new image at %s, adding to the DB" % str(image_path)
            create_log(message2, 1)
            data.make_image(image_name, image_path, image_size)
