# SLMocapArchive
Collected Sign Language Motion Capture

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24149408.svg)](https://doi.org/10.5281/zenodo.24149408)

Hello, this is Studio Galt. Since 2020 we have been recording motion capture, primarily of American Sign Language (ASL). Everything here is free under CC0.

**[Browse the signs](https://studiogalt.github.io/Sign-Language-Mocap-Archive/)** Search the archive, watch each sign, and download its files without cloning anything.

**At a glance:** about 2,700 motions covering 2,100+ signs, plus the ASL fingerspelling alphabet and numbers. Each motion comes as FBX for Blender, Unreal and Mixamo-style rigs (and loads in Unity and Maya), with a rendered video and a ReadMe. See [catalog/SUMMARY.md](catalog/SUMMARY.md) for current counts and coverage.

1. [Quick start](#quick_start)
2. [Finding a sign](#finding)
3. [Downloading only what you need](#downloading)
4. [What's in a motion folder](#motion_folder)
5. [Reporting an error or requesting a sign](#errors)
6. [General FAQ](#general_faq)
7. [Tech FAQ](#tech_faq)
8. [Avatar FAQ](#avatar_faq)
9. [File FAQ](#file_faq)

<a name="quick_start"></a>
## Quick start

1. Find your sign in the [gallery](https://studiogalt.github.io/Sign-Language-Mocap-Archive/), or in the [catalog](#finding) (use the row whose `status` is `current`).
2. Download just that folder ([how](#downloading)).
3. Pick the FBX for your target:

| I'm using… | Use this file |
|---|---|
| Blender, with the Galtis avatar | `… Mesh.fbx` (or the `.blend` in *Blend File*) |
| Blender Rigify | `… Rigify APose.fbx` / `… Rigify TPose.fbx` |
| Unreal Engine 5 | `… Manny` / `… Quinn` / `… MetaHuman` FBX (newer motions) or `… No Mesh UE Mannequin.fbx` (older) |
| Mixamo-compatible rigs, Unity | `… No Mesh Mixamo.fbx` or `… Mixamo TPose.fbx` |
| Research / your own retargeting | `… No Mesh Full.fbx` (every bone), or the raw take in *FBX Files/Original* or *Raw Mocap* |

Not every motion has every file. The file set changed over the years (see [Folder layouts](#layouts)), and the catalog lists exactly what each motion has.

<a name="finding"></a>
## Finding a sign

[`catalog/catalog.csv`](catalog/catalog.csv) lists every motion, one row each. It opens in any spreadsheet, and GitHub lets you search it in the browser. [`catalog/catalog.json`](catalog/catalog.json) has the same data for scripts.

Useful columns:

| Column | Meaning |
|---|---|
| `name`, `group` | The sign as named in the folder; `group` gathers alternates (Alt 1, Var, 2, …) of the same sign |
| `date` | Upload date (ISO format, so it sorts correctly) |
| `status` | `current`, or `superseded` when the same motion was re-made under a newer date (`superseded_by` says which) |
| `folder` | Where it lives in the repo |
| `layout` | Which [folder layout](#layouts) it uses |
| `rig`, `blender_version` | Galtis rig version and Blender version it was made with |
| `raw_mocap_file` | The raw take it was cleaned from, when known |
| `raw_mocap_source` | How that link was found: `readme` (the ReadMe's Original Motion), `bundled` (the copy in *FBX Files/Original*), or `name match` (a Raw Mocap file with the sign's name; checked against the ReadMe links, it agrees over 99% of the time) |
| `keypose_frames` | Key pose frame numbers from the ReadMe |
| `facial_animation` | `yes` if face shape keys move beyond blinking, `no` if only blinks, `unknown` for motions whose ShapeKeys file has no key names (mostly 2023) |
| `has_…` columns | Which file types exist for that motion |

The catalog is rebuilt automatically on every push by [`tools/build_catalog.py`](tools/build_catalog.py). Anything that looks misnamed or incomplete goes to [`catalog/issues.csv`](catalog/issues.csv).

<a name="downloading"></a>
## Downloading only what you need

The full archive is very large, so cloning everything isn't practical. Git can download just the folders you want:

```bash
git clone --filter=blob:none --sparse https://github.com/StudioGalt/Sign-Language-Mocap-Archive.git
cd Sign-Language-Mocap-Archive
git sparse-checkout set "SG ASL Dictionary/ASL C/SG ASL Cabinet 2025-2-12 Upload"
```

Copy the folder path from the `folder` column of the catalog. To add more folders later, run `git sparse-checkout add "<folder>"`.

Without git: [DownGit](https://downgit.github.io/#/home) downloads a single folder as a zip. Paste in the folder's GitHub URL. There is a [DownGit walkthrough](Documentation/Workflows/DownGit%20Workflow%20%28How%20to%20download%20specific%20files%29.md) in Documentation, and more guides (Maya, Unreal, Rokoko) in the [Documentation index](Documentation/README.md).

<a name="motion_folder"></a>
## What's in a motion folder

Each motion is a folder named `SG ASL <Sign> <Date> Upload`. The newest layout (2026) looks like this:

```
SG ASL <Sign> <Date> Upload/
├── Blend File/       Working.zip: the Blender file used to make the motion
├── Documentation/    ReadMe.txt, ShapeKeys.txt, Framelog.txt, captioned video (.webm)
├── FBX Files/
│   ├── Full/         Mesh.fbx: Galtis with mesh and every bone
│   ├── Mixamo/       Mixamo-compatible skeleton (most motions)
│   ├── Original/     the raw take before cleanup
│   ├── Rigify/       Rigify A-pose and T-pose
│   └── Unreal_Engine/ Manny, Quinn and MetaHuman, A-pose and T-pose
└── Poses/
    ├── CSV/          bone transforms for each key pose
    └── JSON/         the same poses for JSON Pose Manager (jpm)
```

<a name="layouts"></a>
### Folder layouts

The layout has improved over time. Older folders are left as they were so existing links keep working.

| Layout | Used | What's different |
|---|---|---|
| v1 | 2023 (and the 2023 fingerspelling) | All files loose in one folder: Mesh, No Mesh Full/Mini/Mixamo FBX, MKV and captioned MP4, ReadMe, ShapeKeys |
| v2 | Nov 2023 – Apr 2024 | *Documentation* and *FBX Files* subfolders; *Poses* added in 2024 |
| v3 | Apr 2024 – Mar 2025 | FBX split into *Game Ready* (Mesh, Mixamo, UE Mannequin, Rigify) and *Research* (Full, Mini, UEPlus); pose JSON; GIF; *Blend File* from Jan 2025 |
| v4 | Mar 2025 – Jan 2026 | FBX grouped by target: *Full*, *Mixamo*, *Rigify*, *Unreal_Engine* (Manny, Quinn), *Other* (Mini, UEPlus, until Dec 2025); the GIF is no longer included from mid-2025 |
| v5 | Jan 2026 – now | Adds *FBX Files/Original* (raw take), MetaHuman FBX and *Poses/CSV*; Mini, UEPlus and the pose .blend libraries are no longer included |

<a name="errors"></a>
## Reporting an error or requesting a sign

If a sign is wrong or a file doesn't load, please [open an issue](../../issues/new/choose) using the **Sign correction** or **File problem** template. Corrections are re-recorded under a new date ([General FAQ 12](#general_faq)), and the catalog marks the old one as superseded.

Missing a sign? Use the **Request a sign** template, or add a 👍 to an [existing request](../../issues?q=is%3Aissue%20is%3Aopen%20label%3A%22sign%20request%22%20sort%3Areactions-%2B1-desc). The most-wanted signs are recorded first.

Every sign has its own page you can link to, for example [Cabinet](https://studiogalt.github.io/Sign-Language-Mocap-Archive/sign/cabinet-2025-2-12/). Use **Copy link** in the gallery to get it.

If you use the archive in research, please cite it:

> Studio Galt (2026). *Sign Language Mocap Archive* (Version 2026-11-11) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.24149408

GitHub's **Cite this repository** button gives the same citation in other formats, from [CITATION.cff](CITATION.cff). The [Zenodo record](https://zenodo.org/records/24149408) holds a permanent copy of the catalog, documentation, pipeline scripts and rig; the motions themselves are here on GitHub. Citing is appreciated, not required: everything is CC0.

---

<a name="general_faq"></a>
## GENERAL FAQ

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

<a name="tech_faq"></a>
## TECH FAQ

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

We don't have access to every piece of software, but Blender is very good at interoperability. If there's software you'd like us to test with, [open an issue](../../issues/new/choose).

7) What are your export formats?

FBX is our primary format. We want to expand into glTF and USD. USD is an open format created by Pixar and is being adopted across much of the 3D industry.

8) Facial data?

ASL and other sign languages use facial movements to convey tone and information. Some signs require facial movement to be complete; for others it adds extra information (similar to punctuation or vocal tone). Because there is a wide range of possible tones, facial data is usually left blank unless the sign requires it. The catalog's `facial_animation` column shows which motions have it.

9) How do I change her face?

Shape keys, sometimes called blendshapes. Select the GaltisHead object and open the Data tab (green triangle on the right). You will see a list of shape keys following FACS (the Facial Action Coding System). Move the values between 0 and 1 to see the face perform each movement.

10) Where are your tutorials?

See the [Documentation index](Documentation/README.md) for workflows in Maya, Unreal (mannequin and Mixamo characters) and Rokoko. If you have something to share, or want something covered, let us know.

<a name="avatar_faq"></a>
## AVATAR FAQ

1) Who is the Avatar?

Her name is Galtis. Very creative. But we stan.

2) Why is she a girl?

Hatsune Miku demands it. The real reason: part of the cleanup process is making sure the mesh doesn't intersect itself, which is more likely to happen on a female avatar than a male one. If intersections are fixed for the female avatar, they should be fixed for a male avatar too.

3) Can I use her in X?

She is open source and free to use. Please, no crimes.

4) What is the rig flow?

The animator manipulates FK and IK bones, which move an intermediate rig. The intermediate rig has correction bones that help it deform more naturally. Finally, the correction bones and intermediate bones drive the deform rig that goes into Unreal. All the deform rig does is translate the axes from Blender's standard to Unreal's.

Rig versions are in the [Rigs](Rigs) folder, named by date (`Galtis 8 YYYYMMDD.blend`). Each motion's ReadMe and the catalog's `rig` column say which version it used.

<a name="file_faq"></a>
## FILE FAQ

1) There is a lot going on in each folder.

Correct. Let's break it down. (Folder names vary by era; see [Folder layouts](#layouts).)

2) What is in the Documentation folder?

The MKV is a video of the rendered animation, and the MP4 (or, in newer motions, the WebM) is the same video with captions. That in turn becomes the GIF used on social media. The ShapeKeys text file shows which shape keys are active and when, so you can recreate the face movements. The ReadMe lists the Blender version, rig version, date, the original take, and all key pose frames. Newer motions also have a Framelog, which records any frame-range adjustments made during cleanup.

3) What is in the Poses folder?

The JSON folder has a JSON file for every key pose, listing all bone positions. These work with JSON Pose Manager (jpm) for Blender, and can be used for non-jpm purposes too.
<!-- TODO: add the JSON Pose Manager affiliate link here -->
Newer motions also have a CSV folder with the same key poses as plain spreadsheets, including Rigify metarig versions (`metarig A` / `metarig T`).
The .blend files (in older layouts) contain nothing but the pose assets. You can append them to your own copy of the rig to access the poses. The Mixamo one is exactly the same, but with Mixamo bone mapping.

4) What is in the FBX folder?

It depends on the era (see [Folder layouts](#layouts)), but the files are the same family:

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

No. See [Downloading only what you need](#downloading).

6) What is the Raw Mocap folder?

The uncleaned recordings, in numbered batches. The file name is the take name plus its frame range, e.g. `SG ASL Cabinet_2078-2645.fbx`. Batches 3–6 also contain `_frames_` re-cuts of many takes (e.g. `SG ASL Black_frames_521-1294.fbx`); the cleaned motions were almost always made from the plain cut. A motion's ReadMe ("Original Motion") and the catalog's `raw_mocap_file` column point to the take it came from.

7) What are the scripts in Documentation/Scripts?

The Blender scripts used to build each motion, from import through bundling (the 2026 versions, plus the July 2024 ones for reference). See [Documentation/Scripts/README.md](Documentation/Scripts/README.md) for set-up and order.
