# SLMocapArchive
Collected Sign Language Motion Capture  
  
Hello this is Studio Galt. Since 2020 we have been recording Motion Capture, primarily of American Sign Language. I'm going to run the rest of the ReadMe as an FAQ.
1. [General FAQ](#general_faq)
2. [Tech FAQ](#tech_faq)
3. [Avatar FAQ](#avatar_faq)
4. [File FAQ](#file_faq)

<a name="general_faq"></a>
## GENERAL FAQ

1) What's the License?

CC0, we don't reserve any rights, use this as you feel. We want to make these assets free for everyone.

2) CC0 forever?

Yes, unless we are forced by law to change. So please no crimes.

3) Why Sign Language?

It hadn't been done, or not publicly available. Also, we mainly do ASL (American Sign Language).

4) Why ASL?

I'm in English speaking North America.

5) Speaking, you are not Deaf?

Nope, I am hearing person, my knowledge of ASL is not complete.

6) Why would I come to you for translation then?

You shouldn't. I do not offer translation services. I offer the ability to turn translation into animation. Once in a digital format there is a lot that can be done quite easily. Change character, change angle, change speed. Digitzation does not solve all problems but has its advantages.

7) I speak English, why don't I just do it myself?

That would be SEE (Signed Exact English) not ASL. That may be appropriate for your project or not, depending on what project is. Like a dictionary it can teach certain things about a language, but not others.

8) Do you intend to do other languages?

We try to do the base alphabets for as many languages as we can but to another full language, I would require sponsorship and assistance with the language.

9) Sponsorship?

This is not my fulltime job, but I would like it to be. We will fight to keep the resources free and CC0 in any case.

10) What do you mean language assistance?

Most Sign Language resources are written in the local spoken. I can do ASL and BANZL (British, Australian and New Zealand Sign Language) because the resources are in English, but doing it without knowing the spoken language will increase errors exponentially.

11) Errors?

While 100% accuracy is the goal, mistake can and will happen. Yet another reason we recommend using professional translation. We do have system for correcting errors.

12) How do you correct errors?

Every file has date on it, when an error is found, we receate the motion under a new date. We try to avoid deleting old motions, even if incorrect, because we believe it is important be able to reproduce any results (even the errors). General rule of thumb, newer is more accurate. 

13) Can I use the motions for non-sign language purposes?

Yes, but these motions are part of a language as such it has meaning or context can confuse and annoy people (see Neon Genesis Evangelion). A good way around this is modify it to be less likely to mistaken for something they shouldn't be.

14) We can modify these files?

Absolutely. That is point of this project. Retarget to your characters.

15) Can I use this for other languages other than ASL?

If you know a sign in another language matches an ASL one, or how to modify an existing motion to do so go for it. Please advise us as well, if this project ever does tackle other languages being able to reuse existing motions would be a great aid.

16) Can use this for machine learning (AI)?

We need to break this into sub points cause that's a big category.

16a) AI translation?

ASL and English are differnet languages so automatic translation will be difficult. It is definitely the long term goal for great translation, automatically generated. However, in terms of time line that could be available from tomorrow to never.
There is definitely a value in fast but dubious quality translations, the popularity of anime across the globe is proof of this. If someone says the automatic translation are not desireable for themselves please respect their wishes.

16b) AI art?

For Art AI, yes, but we please respect other artists decision to not want to be used for AIs Art.

16c) Are you using AI?

Maybe. The Xsens, and Stetchsense have algorithms to smooth and correct data, as I do not know their internal systems, I cannot say for sure. Coding is AI assisted, and there plans for AI automations.

16d) AI automation how so?

The workflow now exports records of change in layers as CSV. Using Reinforcement Learning to predict where edits are going to speed up cleanup.

17) Can we use them for NFT?

Yes, but we will not endorse any NFT projects. We are for maximum access to everyone, where NFT are about controlled access. This is not a bad goal, but it is not our goal.

<a name="tech_faq"></a>
## TECH FAQ

1) What do you record at?

All recordings are done at 240 frames per second. However, we post at 60 frame per second.

2) Why change fps (frames per second)?

Limiting the size of the files, and reducing clean up time.

3) What is your equipment?

I use Xsens Link suit, and StretchSense Gloves.

4) Are you sponsored by them?

No, but I would like to be.

5) What Software do you use?

Blender is the primary, it's free and open source. One of the goals of this project is create sign avatars at 0 cost or as close as possible, naturally Blender has  We do occasional quality checks to make sure files load into Autodesk Maya, Nvidia Omniverse, Unity and Unreal Engine. But not every motion will be checked. If something does not work please let us know!

6) What about X software?

We don't have access to every software, but Blender is very good at interoperability.
If you have a software you would like to 

7) What are your export formats?

FBX is our primary. We want to expand into GLTF and USD>
USD is open format create by Pixar, and is being adopted many parts of the 3d industry.

8) Facial data?

ASL and other sign languages use facial movements convey tone and information. Some signs require facial movement to be complete, other it adds extra information (similar to punctuation of vocal tone). Because there are a wide range of tones, the facial data is usually left blanket unless required to complete the motion.

9) How do I change her face?

Shapekeys, sometimes called Blendshapes. Under the GaltisHead Object, click on the data tab (green triangle on right), you will a list of shapekeys, following the FACS (Facial Action Coding System) measurement system. Move the numbers from 0-1 to see face perform the movements.

10) Where are your tutorials?

Under documentation, if you have something or want something let us know.

<a name="avatar_faq"></a>
## AVATAR FAQ

1) Who is the Avatar?

Her name is Galtis. Very creative. But we stan.

2) Why is she a girl?

Hatsune Miku demands it. The real reason is part of the clean up process is making sure the mesh doesn't intersect itself. This is a more likely to happen on a female avatar than a male avatar. If the avatar intersections are fixed for female, it should be fixed for a male avatar.

3) Can I use her in X?

She is opensource and free to use. Please no crimes.

4) What is the rig flow?

FK and IK bones are manipulated by animator, and move intetmediate rig. The intermediate rig has correction bones that helps the bones deform more naturally. Finally correction bones, and the intermediate bones go into unreal (deform rig). All the deform rig does is translate the axis from blender standard to unreal standard.

<a name="File_faq"></a>
## File FAQ

1) There is a lot going in each folder.

Correct. Let's break it down:

2) What is in Documentation folder?

MKV is a video of render animation, MP4 is the same video with Captions, that in turn becomes the GIF that is used on social media sites. The Shapekeys text file, shows which shapekeys are activated when to make sure you can recreate face movements. And lastly the ReadMe, includes version of blender, Rig version, date, and list of all keypose frames.

3) What is in the Pose Folder?

The JSON folder is a series of JSON files for every keyposes that lists all bone positions. It works with Jason Pose Manager, which is available on Blender. 
Here is my affilate link (a percentage of purchase through this link goes to the project):
JSON files can be used for non-JPM purposes. 
Next is blend files, these include the nothing but the pose assets. You can append to your own copy of rig, and access the poses. The mixamo is the exact same but under mixamo mapping.

4) What is in the FBX folder?

Two sets of folders, game ready, and research. Game ready includes the mesh assets with all bones (that is almost 400 at time of writing). This is probably overkill but its there. Next is No Mesh Mixamo, matchinbg the Mixamo rig, with the addition of a locator root. Lastly is UE mannequin, designed to match Unreal Engines Mannequins.
The other folder is research, still useable for other purpose but are heavier. No Mesh Full, has every bone the full version does but no mesh. The UEplus is the Unreal Mannequin with additional correction bones. And the No Mesh Mini is very similar to the Mixamo one, with different names (in case Adobe requests we stop mapping in Mixamo, we will transition to No Mesh Mini). 

5) Do I have to download the entire XXXGB archive to get the file I want?

Me personally, I use downgit (https://downgit.github.io/#/home) 
Link to workflow:
https://github.com/StudioGalt/Sign-Language-Mocap-Archive/blob/main/Documentation/Workflows/DownGit%20Workflow%20(How%20to%20download%20specific%20files).docx 