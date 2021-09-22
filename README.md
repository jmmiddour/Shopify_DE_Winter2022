# PhotOPT - A web-based Application 
PhotOPT is an image repository. Users can upload images in their account and make them publicly viewable or for private use only. 

This repository also gives all users access to other user's images that they mark as publicly sharable. To view these publicly sharable images, you do need to set up an account though. We want to keep all these images within the community.

## Current Features Available:

- Register for an account to store your images in
  ![](https://raw.githubusercontent.com/jmmiddour/Shopify_DE_Winter2022/main/static/register_route.jpg)
- Log in and out of that account to protect your images
  ![](https://raw.githubusercontent.com/jmmiddour/Shopify_DE_Winter2022/main/static/login.jpg)
- Get a quick look at up to the 10 most recently upload images right on your home page
  ![](https://raw.githubusercontent.com/jmmiddour/Shopify_DE_Winter2022/main/static/login_conf.jpg)
- Upload more images to store safely in your account
  ![](https://raw.githubusercontent.com/jmmiddour/Shopify_DE_Winter2022/main/static/upload_img.jpg)
- Keep your images private or make them public and allow other users see them too
- Delete an image you no longer want
  ![](https://raw.githubusercontent.com/jmmiddour/Shopify_DE_Winter2022/main/static/delete_img.jpg)
- View just a single image with its details
  ![](https://raw.githubusercontent.com/jmmiddour/Shopify_DE_Winter2022/main/static/display_img1.jpg)
  ![](https://raw.githubusercontent.com/jmmiddour/Shopify_DE_Winter2022/main/static/display_img2.jpg)
- View all images currently in stored in your account
  ![](https://raw.githubusercontent.com/jmmiddour/Shopify_DE_Winter2022/main/static/all_imgs.jpg)

## How to Use this Application:
I have made it super easy to use this application. The only thing you need to run this application is a computer with `python 3.8` and a terminal. Then just follow these simple steps:
1. Clone this repository to your machine.
2. Navigate to the location on your machine where this cloned repository lives now.
3. This repository includes a `Pipfile` and `Pipfile.lock`, which holds the dependencies needed for the application to run. To set up the `pipenv` on your machine:
   1. If the newest version of Python you have on your machine is `python 3.8`:
      1. Use the command `pipenv install --dev` in your terminal.
      2. Then `pipenv shell` to launch into the pip environment.
   2. If you have a newer version of Python on your machine, you will have to specify the version of Python to use:
      1. Use the command `pipenv --python 3.8 install --dev` in your terminal.
      2. Then `pipenv shell` to launch into the pip environment.
4. Finally, just type `python app.py` in your terminal to run the Flask application.
5. You will see the hyperlink to click that will take you to the website where you can navigate the application. The address should be `<localhost>:5000`.

## Future Implementations to Come:
All the features that are currently built out right now, I did in just 1.5 days. Given more time, I have so many more ideas for features that will help make this a more useful tool for users. Here is a list of some things I would like to implement with more time in the future:

- A route where all users can view all images that other users marked as being public
- Include a search function on the above route so a user can search all the publicly shared images by name.
- Add more details to the `upload` route that the user can add when adding their image. Such as geolocation, keywords, people in the image, etc.
- Add a second confirmation for the delete image functionality so the user needs to confirm their intent to delete the image to avoid "accidental" deletion of an image.
- Implement a better testing suite when I have more time research the proper way to test certain route functionality.
