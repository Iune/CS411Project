# CS411Project

## Accessing Amazon EC2 Instance

To access the AWS instance where the project is being hosted, download the SSH key from the Facebook group chat. It should be called ```cs411-project.pem```. To set the permissions for this file so that you can use it to SSH into the instance, you will need to run ```chmod 400 cs411-project.pem``` in the folder where you saved the ```.pem``` file.

Now, you can just SSH into the EC2 instance by typing ```ssh -i "cs411-project.pem" ubuntu@ec2-52-38-132-169.us-west-2.compute.amazonaws.com```.

## Editing and Updating the Repository on the EC2 Instance

To edit the project and test your changes on the server, you can simply edit the files there as you normally would. However, after you save the changes, you will need to restart the Apache server before your changes will be visible. To do this, simply run ```sudo apachectl restart``` after saving your changes. You can now refresh your browser and the changes should be visible.

Before committing the code back to the repository, you will need to update the copy on the EC2 instance to update it with any changes that may have been made to the GitHub repository since the last commit. To do this, simply run ```git pull``. 

Now, you can just run ```git commit -m "Message"``` and ```git push``` as you normally would. As far as I can tell, the repository should be configured for my (Aditya) GitHub account (i.e. my name + email configured for the commits), if you run into issues trying to commit I'll see if there is a way to change this.

## Structure of the Flask Project

The Flask application structure is relatively simple. 

* Accessing the database and routing the requests to the application is all handled inside ```app.py```. 
* The templates used for the web pages are found in the ```templates/``` folder. These templates are Jinja2 templates, so you may want to look up syntax for ```for``` loops and ```if``` statements if you are not sure.
* "Static files" for the application (i.e. CSS and Javascript files used for the templates) are found in the ```static/``` folder.
