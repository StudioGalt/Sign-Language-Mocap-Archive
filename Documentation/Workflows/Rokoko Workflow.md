# Rokoko Workflow

_Converted from the original Word document in this folder._

Start with vanilla blender

![Screenshot](images/rokoko-workflow/media/image1.png)

Delete the default cube to show, then click scripting workspace tab.

![Screenshot](images/rokoko-workflow/media/image2.png)

Copy the script from this link:

<https://github.com/StudioGalt/Sign-Language-Mocap-Archive/blob/main/Documentation/Scripts/1)%20Importer%20Rokoko%2030fps.py>

Paste it in the text editor.

![Screenshot](images/rokoko-workflow/media/image3.png)

Go to line 14, and update your working directory.

I have downloaded two set of free mocap from the rokoko site.

![Screenshot](images/rokoko-workflow/media/image4.png)

Unzip them and move them have them in working folder.

It should look something like this.

![Screenshot](images/rokoko-workflow/media/image5.png)

In your working folders, right click, then click on properties.

![Screenshot](images/rokoko-workflow/media/image6.png)

Take copy the highlighted information.

![Screenshot](images/rokoko-workflow/media/image7.png)

Now back in blender, make sure our working folder matches, where the script is looking, adding a double blackslash

C:\Users\Courtland\Desktop\Rokoko becomes this

RenderSpace=( C:\\Users\\Courtland\\Desktop\\Rokoko)

Now run the test script.

Expected result:

If all goes well you should have your armature imported, given a locator.

![Screenshot](images/rokoko-workflow/media/image8.png)

Under pose mode, the locator bone under custom properties there are some custom properties.

![Screenshot](images/rokoko-workflow/media/image9.png)

The custom properties, tell you when started the final, what is the source motion, and which version of blender you were using.

The file should be in 60 fps, as well the scene being set to 60 fps.

![Screenshot](images/rokoko-workflow/media/image10.png)

In your working folder you should have a folder matching the file name.

![Screenshot](images/rokoko-workflow/media/image11.png)

![Screenshot](images/rokoko-workflow/media/image12.png)

In the folder you will have your current blender file, saved to match the file name, and original file.
