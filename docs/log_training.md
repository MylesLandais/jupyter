### 2025-08-17
250817-sh4nn0n-6bit32rank
- tired of fixing dataset
- issues with resolution size? bad cropping
	- cropped for a vertical, 9:16/ style iphone not true 1024x1024
	- should we bias across a few resolution types? we cut up a nice 16:9 image
- pretty good captioning with GLM, needs refinement
- duplicates in dataset, probably need to get some diversity
- tagged tiktok watermark :(
logs
```
100%|##########| 32/32 [00:00<00:00, 51345.73it/s]

  -  Found 32 images

Bucket sizes for /app/ai-toolkit/datasets/sh4nn0n:

640x1120: 32 files

1 buckets made
```

- note to self (spot instance crashed)
- 500 steps not really showing any signs of improvement or likeness being trained 
- Need to fix our dataset folder (curate ~30images)

>! ISSUE: open // problem with runpod "spot" instance getting lost - unable to recover - training wasn't good but we had lora training on 48gb vram instance

- lost training logs after 500steps, not impressed.jpg

### 2025-08-13
- `/app/ai-toolkit/datasets/syl/23-07-29_13-39-49_0408.mov_snapshot_00.00.12__23.07.30_09.02.50_.png`
- 2025_08_13-sh4nn0n-Qwen
- not sure what dataset i used, bad captions
- i think it was `2024-07-02/img/16_samber`
- fucked up activation and fix captioning style
make dataset with hugging face
 
## 2025-07-07
- https://medium.com/@zhiwangshi28/why-flux-lora-so-hard-to-train-and-how-to-overcome-it-a0c70bc59eaf
	- Guide for training flux lora models 
	- 
# 2025-06-05
- Backing up dataset files
- problem with : and 

# 2025-05-30
- https://www.reddit.com/r/StableDiffusion/comments/1kyhepz/if_i_train_a_lora_using_only_closeup_facefocused/
	- train bias & weights
- Release Target Date: Easter (Spring Major)
	- Focus on Bunny Girl Cosplay
	- see [[2025-calendar]]
- [[2025-01-26]
	- Working with AIstudio to synthesis knowledge base article
	- testing x2048 image resolution against SDXL+illustious settings
		- NOT USING PRODIGY
	- very slow, will take ~6 hours at 3it/s to complete
	 - changed settings a little further and it/s went down again...
	 - 2:58:37<31:42:17, 11.90s/it, avr_loss=0.0702]
	 - file size is almost 500mb, need to trim this down --
	 - 
steps:   9%
	-   num batches per epoch / 1epochのバッチ数: 1312
	- letting run overnight
	- can probably shorten filenames
	- 
# 2025-01-25
- training resolution using 2048x buckets instead of 1024 (will increase training time and vram req)
- Image Generation (sampling and evaluating your lora)
	- Samplers [refrence](https://www.reddit.com/r/StableDiffusion/comments/16wykzy/ever_wondered_what_those_cryptic_sampler_names/)
	- DPMPP2m + Beta Sampler
	- cfg 2.5
	- 
# 2025-01-05
	- image_text_schema
	
# 2025-01-01

- Tracking prompts and schema for image_text 
- updating sha4nn0n to 32 images?
- schema_update_
- [[schema_image_text]]
- [[dataset_sil]]
- [[dataset_unsorted]]
- [[dataset_triangl_girls]]
# 2024-12-23
- how to save your env token for HF+toolkit
    `hf_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX # REDACTED` # Token redacted for security
- p0ppy project
- first take not great sample (need to review in comfyui)
- trying a version with mannequin

"prompts" " [
    "Victoria secret angel, bombshell model, doutzen wearing a Triangl Poppy Sorbet bikini, posing in a professional photography studio"
    "photo of a mannequin wearing a triangl poppy sorbet bikini"
    "A teenage VSCO girl on a sandy beach wearing a triangl poppy sorbet bikini posing with a silly expression making a peace sign with her right hand"
]
- problem with not tracking dataset lol
- looking for 30image sets
# 2024-12-08
- (missing/todo) Write .env for hf-cli token?
- unable to find nvidia gpu from container...
- interactive session attach (missing logs from training/python output)
-         "prompts": [
            "sh4nn0n wearing a plain white tshirt",
            "sh4nn0n in a black bikini, hair in a top bun",
            "sh4nn0n making a peace sign with her hands, eyes closed, sticking her tongue out, silly photo"
        ],
- running a no_cap experiment to a/b test
- another experiment
    - bumping up the step count to maximum 4096
    - probably over cooks but ???
- results on 1k steps with caption -- within exceptable range
- tested model has a bias towards (eyes) and (jewlery)

# 2024-11-29
- Curating a dataset
	- Videos from TikTok
	- 6817922073944395013
		- Snap at specific timestamps
	- /edits
		- [6817922073944395013]-[00:00:06.340]v1
			- Needs Crop
		- `23-06-03 19-58-36 0238.mov_snapshot_01.54.973.jpg`
			- Rotate
			- Crop
			- Captioning Time?
- Look at training specific Layers
- 
## 2024-11-26
[[lora-training-flux]]
continue andrea's youtube video
lora training
- Network Rank Parameter !!!
- *Good loras can be less than 4.5mb* (128dim) @u-yacben
	- https://www.reddit.com/r/StableDiffusion/comments/1f523bd/good_flux_loras_can_be_less_than_45mb_128_dim/
```
      network_kwargs:
        only_if_contains:
        - transformer.single_transformer_blocks.7.proj_out
        - transformer.single_transformer_blocks.20.proj_out
```
- trained on blocks 7 & 20

- Charecter design sheet
	- Black Tights
		- 
	- Black Leggins?
## 2024-11-25
- Flux Loras (Basic to advanced) by Andrea Baioni
	- took 72gb of vram
- train_lora_flux_24gb vram yaml ai-toolkit/config/examples
- Methodology
	- "DreamBooth method"
	- limited input (as few as 5)
	- using a `trigger phrase`
	- 10 as a starting point
	- image captioning prompts
		- `<trigger word> (description)`
		- Blip style captioning?
	- a100 setup with a jupyter notebook
	- 2000 steps
	- epoch save count and save last (n)
- https://youtu.be/HzGW_Kyermg
	- Copy example config
	- Investigate triggerword and leaving it commented out?
	- save_every 200steps
	- max_steps_to_keep 4
	- only allow .jpg or .png
		- png for transparency?
- https://youtu.be/F-7gfqSP2ZY
	- use llava model for basic captioning?
	- comfy ui workflow using "florance model" [[workflows]]
	- 
### Work on dataset
- `23-11-23 10-04-45 0801.mov_snapshot_00.02.04_[23.11.23_18.44.12]` crop and focus for x1024
## 2024-11-24
- *entering winter era*
- Spinning up an `ai-toolbox` container
- build process uses runpod-docker as a base
- [[setup-vscode]]
	- broken on wayland
- https://www.youtube.com/watch?v=Z_nF4MRsPHY
	- Kohya-ss "quick start"
	- 15-100 images
	- 1024x1024
	- quality images resolution, focus on model
	- n_imageclass
	- Caption images with utilities wd14
	- testing with comfyui
	- lora loader
	- cfg 1 sampler beta?
- https://youtu.be/d9ZyvxZEkHY
	- fluxgym runpod :(
- https://youtu.be/bN2uhrVKdPE
	- AI Toolkit setup in workspace
- missing dependency flux_dev for training workspace
- prompts for testing (double in comfyui plots)
	- Hands Test
		- Making a Peace sign with hands
		- Making a 'Loser' sign with hands
		- giving the middle finger
	- Text Test
		- Wearing a white shirt with "hooters" written on the front and a name tag that says "{name}"
		- Wearing a black tshirt with "thrasher" is a fire-style font
	- Charecter outfit tests
		- Mari plugsuit from eva
- Monitor and log Training resource usage & -budget-
	- using ~20gb vram
- 
## 2024-10-02

- Turn off your display for accelerators
> First things first - a little bit about my technical setup and how I train Loras. I'm running locally on a Gigabyte AORUS 3090 24GB, with 64GB RAM and an i7 11700k. I use my integrated graphics card on my motherboard for my display so as not to fill up the precious VRAM on the 3090 (even the tiny amount used to show the monitor makes a difference).
from 

https://civitai.com/articles/7203
- Try No Caption training
- Try "Natural Language" captioning
- booru tags were less performant than NL
- 

This is what you would call a scientific notebook / experiment log for [[sd15-lora-training]] and [[SDXL-Lora-Guide]]

### 2024-08-31 (Spooky Season - Alpha)
- Creating [[lora-training-flux]]

### 2024-07-01
*Birthdays Pride Patriotic*
```
kohya-ss-gui  | NaN found in latents, replacing with zeros
kohya-ss-gui  | NaN found in latents, replacing with zeros
```
base-sdxl training parameters

SDXL
- Cache text encoder output 
- network train unet only
- No Half VAE
-  Gradiant Checkpointing 3
- memory efficient attention

```
AssertionError: network for Text Encoder cannot be trained with caching Text Encoder outputs
```

BF 16
disable cache text encoder output

Testing in comfyui
control groups
multiple loras into XY plots?
https://myaiforce.com/comfyui-lora-plot/

results: lora did not appear to change the image. running v2 using the _samber_ keyword
trigger word was not in captions - Low order of affect
https://followfoxai.substack.com/p/mass-produce-xy-plots-with-comfyui

### 2024-07-02
*continuing summer edition build*
adding trigger word to caption files
increased 8 -> 16 for each epoch image steps
- thinking we have an issue with bucketing images from iphone, try max_resolution 4k 

4k training batch was decent
- would like to add images to dataset
- test using prodigy adapter

### 2024 07 03
Testing prodigy training instead of adamw8b
would like to continue training 2x but maybe after prodigy POC
```

kohya-ss-gui  |                     WARNING  learning rate is too low. If using D-Adaptation or   train_util.py:3982
kohya-ss-gui  |                              Prodigy, set learning rate around 1.0 /
kohya-ss-gui  |                              学習率が低すぎるようです。D-AdaptationまたはProdigy
kohya-ss-gui  |                              の使用時は1.0前後の値を指定してください: lr=0.0001
kohya-ss-gui  |                     WARNING  recommend option: lr=1.0 / 推奨は1.0です             train_util.py:3985
kohya-ss-gui  |                     INFO     use Prodigy optimizer | {}                           train_util.py:4034

```

*need to change the learning rate for prodigy...*
using only 10gib of memory, maybe we could 2-4x our batch size.

kasucast 18- 
training config
metadata?
dataset preperation
advanced parameters
meta_cap.json
meta_lat.json
use full path
https://docs.google.com/document/d/144xqK_QSIbP-yJxQsztgRfm5S80rpK-UUrz0mqLy5gg/edit

cache text encoder? do not train text encoder

Min SNR gamma: 5
Efficient diffusion training paper on archiv

Look at the tensorboard logs ***

n tokens 2 
wandb api key loggin

xy plots eff nodes
warmup 5%

decoupled weight decay regularization
- 
betas default values 0.9,0.999 beta1 and beta2 values 

**additional parameters**
`--network_train_unet_only --lr_scheduler_type "CosineAnnealingLR" --lr_scheduler_args "T-max=25"

Optimizer extra arguments
`decouple=True weight_decay=0.45 d_coef=2 use_bias_corrections=True  safegaurd_warmup=True`

Memory out error 

4k32 - fixing resolution buckets with dims set to 32/32
around 19gib memory

https://rentry.org/59xed3
copying some ideas from the other guide
dadapt - est time to complete ~30 hours for 3k steps



### 2024 07 04
*fourth of july*
testing dadapt options with 64/64

increase image set to 100?

### 2024 07 14
- make sure to kill text gen ui before training
- Downsizing images from 4k -> ~2k
- a 4k iphone image 50% is hd
- may have been missing keep n tokens
- naming issue got 128/128 to run but names 256 ---
- not using memory attention
- try 256/256 with memory attention?
- missing caps after redo...
- https://github.com/bmaltais/kohya_ss/issues/1288#issuecomment-1656665274
- another prodigy conf
- https://github.com/derrian-distro/LoRA_Easy_Training_Scripts
- some training scripts - might be worth reading
- https://huggingface.co/blog/sdxl_lora_advanced_script
- https://minimaxir.com/2022/11/stable-diffusion-negative-prompt/
### 2024-07-15
- Advice from a wizard 
	- > My recommendation is to train a Lora. I don't use Civit Loras because they're all horrible garbage. I collect 80-100 images of the subject, and use QwenVL to caption the images . You could use florence-2 but it doesn't support VQA like Qwen does. This allows you to create great captions. Then I train the Lora for around 7000 steps with kohya, trying to keep as high of a batch size that will fit into VRAM, for 24gb that would be around 4 or 5. It will probably converge around 3500 steps but I'd just keep an eye on the sample images to check your results. Train against the base model and use a good fine tune to create images, I prefer realvisxl.
- fooocus with an inswapper
	- 1) collect 50-100 photos of the subject, you can do fewer but the results aren't nearly as good  
2) run a captioner - i prefer computer vision models to caption for me but you can also manually caption or use a tagger  
3) run a training with kohya or onetrainer. lots of presets out there to try so you don't have to think about it
### 2024-07-16
- Testing Loras, Some resemblance at around 5 Epochs, quickly burnt the lora and gets cursed
- 16_images at 8 epochs should be around ~128 iterations for the systems
- 8_16 would be more epochs -- finer control
- 
### 2024-06-14
*Fathers Day*
- Accelerate Launch issue with koyaa-ss-gui in docker logs

```
2024-06-17 01:41:14 INFO     U-Net converted to original U-Net                sdxl_train_util.py:120
                    INFO     Enable xformers for U-Net                            train_util.py:2660
                    INFO     [Dataset 0]                                          train_util.py:2079
                    INFO     caching latents.                                      train_util.py:974
                    INFO     checking cache validity...                            train_util.py:984
import network module: networks.lora
100%|██████████| 13/13 [00:00<00:00, 102108.52it/s]
                    INFO     caching latents...                                   train_util.py:1021
100%|██████████| 13/13 [00:04<00:00,  2.78it/s]
Traceback (most recent call last):
  File "/app/sd-scripts/sdxl_train_network.py", line 185, in <module>
    trainer.train(args)
  File "/app/sd-scripts/train_network.py", line 293, in train
    network, _ = network_module.create_network_from_weights(1, args.network_weights, vae, text_encoder, unet, **net_kwargs)
  File "/app/sd-scripts/networks/lora.py", line 703, in create_network_from_weights
    if os.path.splitext(file)[1] == ".safetensors":
  File "/usr/local/lib/python3.10/posixpath.py", line 118, in splitext
    p = os.fspath(p)
TypeError: expected str, bytes or os.PathLike object, not NoneType
Traceback (most recent call last):
  File "/home/1000/.local/bin/accelerate", line 8, in <module>
    sys.exit(main())
  File "/home/1000/.local/lib/python3.10/site-packages/accelerate/commands/accelerate_cli.py", line 47, in main
    args.func(args)
  File "/home/1000/.local/lib/python3.10/site-packages/accelerate/commands/launch.py", line 1017, in launch_command
    simple_launcher(args)
  File "/home/1000/.local/lib/python3.10/site-packages/accelerate/commands/launch.py", line 637, in simple_launcher
    raise subprocess.CalledProcessError(returncode=process.returncode, cmd=cmd)
subprocess.CalledProcessError: Command '['/usr/local/bin/python', '/app/sd-scripts/sdxl_train_network.py', '--config_file', './outputs/tmpfilelora.toml', '--log_prefix=xl-loha']' returned non-zero exit status 1.
```

- Enabled Cache Latents
- Cookbook [[jupyter-image-check]]
  
2024-04-05
- last two batches broke
- Lora sd15 test went to NaN and broke loss function?
- prodigy SDXL came out warped...

2024-03-31
- Spring Hopping Easter Bunny Edition
- new source images hottub + white tshirt + v neck
- starting with base sd15 move to dream tomorrow.
- Key prompt was a problem...? use long phrase?
- Resolution x2048
	- Took way to long
	- Possibly 24gb ram...
- network rank 16
- network alpha 8

2024-03-31_2
- 1.84it/s,
- around 8gb memory
- regularization missing?
- results -> massive VAE issue? 
- nan loss

2024-03-31_3
- Playing with learning rate?
- Fixed Regularization
- no xformers?
- A matching Triton is not available, some optimizations will not be enabled.
- mixed precision" to "no
- Use WSL instead of Windows
	- WSL Setup broken
- v 22.6.1 -> v23?
