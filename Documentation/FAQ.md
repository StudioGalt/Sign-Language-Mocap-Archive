# FAQ

Questions about the archive, the recordings, the Galtis avatar and the files. For getting started, see the [main README](../README.md).

1. [General](#general_faq): licence, why ASL, errors and corrections, AI use, versions and names
2. [Tech](#tech_faq): recording, equipment, software, formats, facial data
3. [Avatar](#avatar_faq): Galtis and her rig
4. [Files](#file_faq): what's in each folder and file

<a name="general_faq"></a>
## General

1) What's the License?

CC0. We don't reserve any rights; use this however you like. We want to make these assets free for everyone.

2) CC0 forever?

Yes, unless we are forced by law to change. So please, no crimes.

3) Why Sign Language?

It hadn't been done, or wasn't publicly available. We mainly do ASL (American Sign Language).

4) Why ASL?

I'm in English-speaking North America.

5) Speaking of which, you're not Deaf?

Nope, I'm a hearing person, and my knowledge of ASL is not complete.

6) Why would I come to you for translation then?

You shouldn't. I do not offer translation services. I offer the ability to turn translation into animation. Once it's digital, a lot can be done quite easily: change the character, the angle, the speed. Digitization doesn't solve every problem, but it has its advantages.

7) I speak English, why don't I just do it myself?

That would be SEE (Signed Exact English), not ASL. That may or may not be appropriate, depending on your project. Like a dictionary, it can teach certain things about a language, but not others.

8) Do you intend to do other languages?

We try to do the base alphabets for as many languages as we can, but a full additional language would require sponsorship and help with the language.

9) Sponsorship?

This is not my full-time job, but I would like it to be. We will fight to keep the resources free and CC0 in any case.

10) What do you mean by language assistance?

Most sign language resources are written in the local spoken language. I can do ASL and BANZSL (British, Australian and New Zealand Sign Language) because the resources are in English, but working without knowing the spoken language would multiply the errors.

11) Errors?

While 100% accuracy is the goal, mistakes can and will happen. That's yet another reason we recommend professional translation. We do have a system for correcting errors.

12) How do you correct errors?

Every file has a date on it. When an error is found, we recreate the motion under a new date. We try to avoid deleting old motions, even incorrect ones, because we believe it's important to be able to reproduce any results (even the errors). Rule of thumb: newer is more accurate. The catalog's `status` column does this comparison for you.

13) Can I use the motions for non-sign language purposes?

Yes, but these motions are part of a language, so they have meaning, and using them out of context can confuse and annoy people (see Neon Genesis Evangelion). A good way around this is to modify them so they're less likely to be mistaken for something they aren't.

14) We can modify these files?

Absolutely. That is the point of this project. Retarget them to your characters.

15) Can I use this for sign languages other than ASL?

If you know a sign in another language matches an ASL one, or how to modify an existing motion to match, go for it. Please let us know too: if this project ever tackles other languages, being able to reuse existing motions would be a great help.

16) Can I use this for machine learning (AI)?

That's a big category, so let's break it into sub-points.

16a) AI translation?

ASL and English are different languages, so automatic translation will be difficult. Great automatic translation is definitely the long-term goal, but the timeline could be anywhere from tomorrow to never.
There is definitely value in fast but dubious-quality translation; the popularity of fan-subbed anime around the globe is proof of this. If someone says automatic translations are not desirable for them, please respect their wishes.

16b) AI art?

For art AI, yes, but please respect other artists' decisions not to have their work used for AI art.

16c) Are you using AI?

Maybe. The Xsens and StretchSense systems have algorithms to smooth and correct data, and since I don't know their internals, I can't say for sure. Coding is AI-assisted, and there are plans for AI automation.

16d) AI automation how so?

The workflow now exports records of changes in layers as CSV. The idea is to use reinforcement learning to predict where edits will be needed, to speed up cleanup.

17) Can we use them for NFTs?

Yes, but we will not endorse any NFT projects. We are for maximum access for everyone, whereas NFTs are about controlled access. That's not a bad goal, but it's not ours.

18) Why are there several versions of some signs (Alt, Var, Other, 1, 2…)?

The motion capture equipment was only available for a limited time, so we recorded as many signs as we could. Where there was more than one way to sign a word, or a conflict about which way was right, we recorded every version, and left the nuances of the language to be worked out afterwards.

The labels *Alt*, *Var*, *Other* and the numbers don't mean anything on their own: they only tell the versions apart. They don't say which is more common or more correct. Some versions may turn out to be wrong, outdated or regional, and they stay in the archive until someone who knows can say which is which. If you can, please tell us with a [sign correction](https://github.com/StudioGalt/Sign-Language-Mocap-Archive/issues/new?template=sign-correction.yml) or by suggesting a better name (below).

19) A sign's name is misspelled, unclear, or doesn't match the sign. Can I suggest a better one?

Please do. Use **Suggest a better name** on the sign in the [gallery](https://studiogalt.github.io/Sign-Language-Mocap-Archive/), or the [name suggestion form](https://github.com/StudioGalt/Sign-Language-Mocap-Archive/issues/new?template=name-suggestion.yml). Once a name is accepted, the gallery and the catalog's `display_name` show it, and search finds both the old and new names. The folder keeps the name it was recorded under, so existing links, downloads and citations don't break.

<a name="tech_faq"></a>
## Tech

1) What do you record at?

All recordings are done at 240 frames per second, but we post at 60 frames per second.

2) Why change fps (frames per second)?

To limit file size and reduce cleanup time.

3) What is your equipment?

An Xsens Link suit and StretchSense gloves.

4) Are you sponsored by them?

No, but I would like to be.

5) What software do you use?

Blender is the primary tool. It's free and open source, and one of the goals of this project is to create sign avatars at zero cost (or as close as possible), so Blender was the natural choice. We do occasional quality checks to make sure files load into Autodesk Maya, NVIDIA Omniverse, Unity and Unreal Engine, but not every motion is checked. If something doesn't work, please let us know!

6) What about X software?

We don't have access to every piece of software, but Blender is very good at interoperability. If there's software you'd like us to test with, [open an issue](https://github.com/StudioGalt/Sign-Language-Mocap-Archive/issues/new/choose).

7) What are your export formats?

FBX is our primary format. We want to expand into glTF and USD. USD is an open format created by Pixar and is being adopted across much of the 3D industry.

8) Facial data?

ASL and other sign languages use facial movements to convey tone and information. Some signs require facial movement to be complete; for others it adds extra information (similar to punctuation or vocal tone). Because there is a wide range of possible tones, facial data is usually left blank unless the sign requires it. The catalog's `facial_animation` column shows which motions have it.

9) How do I change her face?

Shape keys, sometimes called blendshapes. Select the GaltisHead object and open the Data tab (green triangle on the right). You will see a list of shape keys following FACS (the Facial Action Coding System). Move the values between 0 and 1 to see the face perform each movement.

10) Where are your tutorials?

See the [Documentation index](README.md) for workflows in Maya, Unreal (mannequin and Mixamo characters) and Rokoko. If you have something to share, or want something covered, let us know.

<a name="avatar_faq"></a>
## Avatar

1) Who is the Avatar?

Her name is Galtis. Very creative. But we stan.

2) Why is she a girl?

Hatsune Miku demands it. The real reason: part of the cleanup process is making sure the mesh doesn't intersect itself, which is more likely to happen on a female avatar than a male one. If intersections are fixed for the female avatar, they should be fixed for a male avatar too.

3) Can I use her in X?

She is open source and free to use. Please, no crimes.

4) What is the rig flow?

The animator manipulates FK and IK bones, which move an intermediate rig. The intermediate rig has correction bones that help it deform more naturally. Finally, the correction bones and intermediate bones drive the deform rig that goes into Unreal. All the deform rig does is translate the axes from Blender's standard to Unreal's.

Rig versions are in the [Rigs](../Rigs) folder, named by date (`Galtis 8 YYYYMMDD.blend`). Each motion's ReadMe and the catalog's `rig` column say which version it used.

<a name="file_faq"></a>
## Files

1) There is a lot going on in each folder.

Correct. Let's break it down. (Folder names vary by era; see [Folder layouts](../README.md#layouts).)

2) What is in the Documentation folder?

The MKV is a video of the rendered animation, and the MP4 (or, in newer motions, the WebM) is the same video with captions. That in turn becomes the GIF used on social media. The ShapeKeys text file shows which shape keys are active and when, so you can recreate the face movements. The ReadMe lists the Blender version, rig version, date, the original take, and all key pose frames. Newer motions also have a Framelog, which records any frame-range adjustments made during cleanup.

3) What is in the Poses folder?

The JSON folder has a JSON file for every key pose, listing all bone positions. These work with JSON Pose Manager (jpm) for Blender, and can be used for non-jpm purposes too.
<!-- TODO: add the JSON Pose Manager affiliate link here -->
Newer motions also have a CSV folder with the same key poses as plain spreadsheets, including Rigify metarig versions (`metarig A` / `metarig T`).
The .blend files (in older layouts) contain nothing but the pose assets. You can append them to your own copy of the rig to access the poses. The Mixamo one is exactly the same, but with Mixamo bone mapping.

4) What is in the FBX folder?

It depends on the era (see [Folder layouts](../README.md#layouts)), but the files are the same family:

| File | What it is |
|---|---|
| `Mesh.fbx` | Galtis with mesh and every bone (almost 400). Probably overkill, but it's there. |
| `No Mesh Full.fbx` | Every bone, no mesh. Heavier, good for research. |
| `No Mesh Mixamo.fbx` / `Mixamo TPose.fbx` | Matches the Mixamo rig, plus a root locator. |
| `No Mesh Mini.fbx` | Very similar to Mixamo, with different bone names (in case Adobe ever asks us to stop mapping to Mixamo, we'll switch to Mini). |
| `No Mesh UE Mannequin.fbx` | Matches Unreal Engine's mannequin. |
| `No Mesh UEPlus.fbx` | UE Mannequin plus extra correction bones. |
| `Manny` / `Quinn` / `MetaHuman` `APose` / `TPose` | Unreal Engine 5 skeletons, in A-pose and T-pose versions. |
| `Rigify APose` / `Rigify TPose` | Blender Rigify skeleton. |
| `FBX Files/Original/…` | The raw take the motion was cleaned from. |

5) Do I have to download the entire archive to get the file I want?

No. See [Downloading only what you need](../README.md#downloading).

6) What is the Raw Mocap folder?

The uncleaned recordings, in numbered batches. The file name is the take name plus its frame range, e.g. `SG ASL Cabinet_2078-2645.fbx`. Batches 3–6 also contain `_frames_` re-cuts of many takes (e.g. `SG ASL Black_frames_521-1294.fbx`); either cut may have been used (checking the working files found the `_frames_` cut behind about one in six motions where both exist). A motion's ReadMe ("Original Motion") and the catalog's `raw_mocap_file` column point to the take it came from.

7) What are the scripts in Documentation/Scripts?

The Blender scripts used to build each motion, from import through bundling (the 2026 versions, plus the July 2024 ones for reference). See [Documentation/Scripts/README.md](Scripts/README.md) for set-up and order.
